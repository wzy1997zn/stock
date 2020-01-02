# stock

It was a practice coded in SDU. Using some ML method to analyse the SH stock index and predicing whether the index will be more or less tomorrow.

Some tech points are followed:

*1* web spider -> get news texts

*2* jieba lib -> split the news to words

*3* tf-idf -> get weights of different words

*4* SVD(lsa) -> normorlize, find the best features

*5* CNN -> fit news features to ups and downs

3 and 4 may be replaced by an embedding layer in NN?
