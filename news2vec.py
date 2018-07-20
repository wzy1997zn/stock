# -*- coding: utf-8 -*-
import jieba
from dbhelper import dbhelper
import sklearn

from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import Normalizer
from sklearn.pipeline import make_pipeline


class newsNLP:
    news = (())
    all_doc_list = []
    tfidf = []
    lsa_result = []
    # 从停用词表中获取停用词
    def get_stopwords(self):
        f = open('stopword.txt',encoding='utf-8', errors='ignore')
        str = f.read()
        stoplist = set(str.split())
        # print stoplist
        return stoplist

    # 获得分词结果
    def get_list_jieba(self):
        # 方便操作 添加到list
        # all_doc = []
        # for doc in df[1]:
        #     all_doc.append(doc)
        # print all_doc[0].decode('gbk','ignore').encode('utf-8','ignore')
        all_doc = []
        for each in self.news:
            all_doc.append(each[1])
        # all_doc_list = []
        # 停用词
        stoplist = self.get_stopwords()
        for doc in all_doc:
            # 使用jieba库分词，并剔除停用词
            doc = doc.replace(" ", "")
            doc_list = [word for word in jieba.cut(doc) if word not in stoplist]
            self.all_doc_list.append(doc_list)
        # for doc in all_doc_list[0]:
        #     print doc

        return self.all_doc_list

    # 读取已经分词好的文档，进行TF-IDF计算
    def Tfidf(self):
        # corpus = []
        # for ff in filelist:
        #     fname = path + ff
        #     f = open(fname + "-seg.txt", 'r+')
        #     content = f.read()
        #     f.close()
        #     corpus.append(content)
        all_doc = []
        for each_doc in self.all_doc_list:
            doc_words_splited_by_blank = ""
            for each_word in each_doc:
                doc_words_splited_by_blank = doc_words_splited_by_blank + each_word + " "
            all_doc.append(doc_words_splited_by_blank)

        vectorizer = CountVectorizer()
        transformer = TfidfTransformer()
        self.tfidf = transformer.fit_transform(vectorizer.fit_transform(all_doc))
        word = vectorizer.get_feature_names()  # 所有文本的关键字
        print()

    def SVD(self,n_components):
        svd = TruncatedSVD(n_components)
        normalizer = Normalizer(copy=False)
        lsa = make_pipeline(svd, normalizer)

        self.lsa_result = lsa.fit_transform(self.tfidf)
        print()

    def get_contents(self):
        coon = dbhelper()
        coon.open('stock')
        sql = 'select id,contents from merge'
        result = coon.select(sql)
        print(result)
        self.news = result
        coon.close()

    def save_lsa_vector(self):
        coon = dbhelper()
        coon.open('stock')
        matrix = self.lsa_result.tolist()
        for i in range(len(matrix)):
            each = matrix[i]
            vector = ''
            for item in each:
                vector = vector + str(item) + " "
            sql = 'update merge set vector = "' + vector + '" where id = ' + str(i+1)
            result = coon.insert(sql)
            # print(result)
        coon.close()



if __name__ == '__main__':
    news = newsNLP()
    news.get_contents()
    news.get_list_jieba()
    news.Tfidf()
    news.SVD(200)
    news.save_lsa_vector()
