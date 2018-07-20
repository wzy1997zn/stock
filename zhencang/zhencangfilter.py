# -*- coding: utf-8 -*-
import tushare as ts
import datetime

class Filter:
    close = []
    date = []
    starts = []
    seq = {}
    deals = []

    def get_data(self,id,start,end):
        data = ts.get_h_data(id,start=start,end=end)
        data.sort_index(inplace=True)
        print(data)
        self.close = data['close'].tolist()
        self.date = data.index.tolist()
        self.seq = dict(zip(self.date,self.close))

    def looking_for_start(self):
        for i in range(len(self.date)-8):
            fit,second_index = self.check1(i)
            if not fit:
                continue
            fit,third_index = self.check3(second_index)
            if not fit:
                continue
            fit = self.check2(second_index,third_index)
            if fit:
                self.starts.append(i)



    def check1(self,index):
        start_close = self.seq[self.date[index]]
        fit = True
        cur_date_index = index
        next_date_index = cur_date_index+1
        for i in range(3):
            cur_close = self.seq[self.date[cur_date_index]]
            next_close = self.seq[self.date[next_date_index]]
            if next_close > cur_close * 0.994:
                fit = False
                return fit,-1
            else:
                cur_date_index = next_date_index
                next_date_index = cur_date_index + 1
        still_drop = True
        while still_drop:
            cur_close = self.seq[self.date[cur_date_index]]
            next_close = self.seq[self.date[next_date_index]]
            if next_close > cur_close:
                still_drop = False
                break
            else:
                cur_date_index = next_date_index
                next_date_index = cur_date_index + 1
        cur_close = self.seq[self.date[cur_date_index]]
        if cur_close >= start_close * (1 - (cur_date_index - index) * 0.01):
            fit = False
            return fit,-1
        return fit,cur_date_index

    def check3(self,index):
        fit = False
        cur_date_index = index
        next_5_index = cur_date_index + 5
        while not fit:
            cur_close = self.seq[self.date[cur_date_index]]
            next_5_close = self.seq[self.date[next_5_index]]
            if next_5_close > cur_close * 1.03:
                fit = True
                break
            else:
                cur_date_index = next_5_index
                next_5_index = cur_date_index + 5
            if cur_date_index - index > 30:
                return fit,-1
        return fit,cur_date_index

    def check2(self,index2,index3):
        rise_count = 0
        drop_count = 0
        for i in range(index2,index3-index2):
            cur_close = self.seq[self.date[i]]
            next_close = self.seq[self.date[i+1]]
            if cur_close < next_close:
                rise_count = rise_count + 1
            elif cur_close > next_close:
                drop_count = drop_count + 1
        if rise_count > 20 or drop_count > 20:
            return False
        start_close = self.seq[self.date[index2]]
        end_close = self.seq[self.date[index3]]
        if abs(start_close - end_close)/start_close < 0.03:
            return True
        else:
            return False

    def get_deal(self,date):
        df = ts.get_tick_data('600848', date=date,pause=1)
        if self.deals:
            self.deals.append(df)
        else:
            self.deals = df



def get_date(start,end):
    # start = '2016-06-01'
    # end = '2017-01-01'
    datestart = datetime.datetime.strptime(start, '%Y-%m-%d')
    dateend = datetime.datetime.strptime(end, '%Y-%m-%d')
    datelist = []
    while datestart < dateend:
        datestart += datetime.timedelta(days=1)
        date = datestart.strftime('%Y-%m-%d')
        datelist.append(date)
    return datelist



if __name__ == '__main__':
    f = Filter()
    f.get_data('600848',start='2015-01-05',end='2018-01-09')
    f.looking_for_start()
    for each in f.starts:
        print(f.date[each])

    # datelist = get_date('2015-05-01','2017-05-01')
    # for each in datelist:
    #     f.get_deal(each)
    # f.deals.describe()