###############################################################
# Customer Segmentation with RFM
###############################################################

# Customer Segmentation with RFM in 6 Steps

# 1. Business Problem
# 2. Data Understanding
# 3. Data Preparation
# 4. Calculating RFM Metrics
# 5. Calculating RFM Scores
# 6. Naming & Analysing RFM Segments


# Bir e-ticaret şirketi müşterilerini segmentlere ayırıp bu segmentlere göre
# pazarlama stratejileri belirlemek istiyor.

# Buna yönelik olarak müşterilerin davranışlarını tanımlayacağız ve
# bu davranışlarda öbeklenmelere göre gruplar oluşturacağız.

# Veri Seti Hikayesi
#
# https://archive.ics.uci.edu/ml/datasets/Online+Retail+II
#
# Online Retail II isimli veri seti İngiltere merkezli online bir satış mağazasının
# 01/12/2009 - 09/12/2011 tarihleri arasındaki satışlarını içeriyor.

# Değişkenler
# InvoiceNo: Fatura numarası. Her işleme yani faturaya ait eşsiz numara.
# Eğer bu kod C ile başlıyorsa işlemin iptal edildiğini ifade eder.
# StockCode: Ürün kodu. Her bir ürün için eşsiz numara.
# Description: Ürün ismi
# Quantity: Ürün adedi. Faturalardaki ürünlerden kaçar tane satıldığını ifade etmektedir.
# InvoiceDate: Fatura tarihi ve zamanı.
# UnitPrice: Ürün fiyatı (Sterlin cinsinden)
# CustomerID: Eşsiz müşteri numarası
# Country: Ülke ismi. Müşterinin yaşadığı ülke.


###############################################################
# Data Understanding
###############################################################

import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)
# pd.set_option('display.float_format', lambda x: '%.5f' % x)

df_ = pd.read_excel("datasets/online_retail_II.xlsx",
                    sheet_name="Year 2009-2010")

df = df_.copy()

df.head()
df.isnull().sum()

# essiz urun sayisi nedir?
df["Description"].nunique()

# hangi urunden kacar tane var?
df["Description"].value_counts().head()

# en cok siparis edilen urun hangisi?
df.groupby("Description").agg({"Quantity": "sum"}).head()


# yukarıdaki çıktıyı nasil siralariz?
df.groupby("Description").agg({"Quantity": "sum"}).sort_values("Quantity", ascending=False).head()

# toplam kac fatura kesilmiştir?
df["Invoice"].nunique()


# fatura basina ortalama kac para kazanilmistir? ,
# (iki değişkeni çarparak yeni bir değişken oluşturmak gerekmektedir)
# iadeleri çıkararak yeniden df'i oluşturalım
df = df[~df["Invoice"].str.contains("C", na=False)]

df["TotalPrice"] = df["Quantity"] * df["Price"]

# en pahalı ürünler hangileri?
df.sort_values("Price", ascending=False).head()

# hangi ulkeden kac siparis geldi?
df["Country"].value_counts()

# hangi ulke ne kadar kazandırdı?
df.groupby("Country").agg({"TotalPrice": "sum"}).sort_values("TotalPrice", ascending=False).head()


###############################################################
# Data Preparation
###############################################################

df.isnull().sum()
df.dropna(inplace=True)

df.describe([0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]).T

###############################################################
# Calculating RFM Metrics
###############################################################

# Recency, Frequency, Monetary

# Recency (yenilik): Müşterinin son satın almasından bugüne kadar geçen süre
# Diğer bir ifadesiyle “Müşterinin son temasından bugüne kadar geçen süre” dir.

# Bugünün tarihi - Son satın alma

df["InvoiceDate"].max()

today_date = dt.datetime(2010, 12, 11)

rfm = df.groupby('Customer ID').agg({'InvoiceDate': lambda date: (today_date - date.max()).days,
                                     'Invoice': lambda num: len(num),
                                     'TotalPrice': lambda TotalPrice: TotalPrice.sum()})


rfm.columns = ['Recency', 'Frequency', 'Monetary']

rfm = rfm[(rfm["Monetary"]) > 0 & (rfm["Frequency"] > 0)]

###############################################################
# Calculating RFM Scores
###############################################################

# Recency
rfm["RecencyScore"] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1])

rfm["FrequencyScore"] = pd.qcut(rfm['Frequency'], 5, labels=[1, 2, 3, 4, 5])

rfm["MonetaryScore"] = pd.qcut(rfm['Monetary'], 5, labels=[1, 2, 3, 4, 5])


rfm["RFM_SCORE"] = (rfm['RecencyScore'].astype(str) +
                    rfm['FrequencyScore'].astype(str) +
                    rfm['MonetaryScore'].astype(str))


rfm[rfm["RFM_SCORE"] == "555"].head()

rfm[rfm["RFM_SCORE"] == "111"]

###############################################################
# Naming & Analysing RFM Segments
###############################################################

# RFM isimlendirmesi
seg_map = {
    r'[1-2][1-2]': 'Hibernating',
    r'[1-2][3-4]': 'At_Risk',
    r'[1-2]5': 'Cant_Loose',
    r'3[1-2]': 'About_to_Sleep',
    r'33': 'Need_Attention',
    r'[3-4][4-5]': 'Loyal_Customers',
    r'41': 'Promising',
    r'51': 'New_Customers',
    r'[4-5][2-3]': 'Potential_Loyalists',
    r'5[4-5]': 'Champions'
}

rfm

rfm['Segment'] = rfm['RecencyScore'].astype(str) + rfm['FrequencyScore'].astype(str)

rfm['Segment'] = rfm['Segment'].replace(seg_map, regex=True)
df[["Customer ID"]].nunique()
rfm[["Segment", "Recency", "Frequency", "Monetary"]].groupby("Segment").agg(["mean", "count"])

rfm[rfm["Segment"] == "Need_Attention"].head()
rfm[rfm["Segment"] == "Need_Attention"].index

new_df = pd.DataFrame()

new_df["Need_Attention"] = rfm[rfm["Segment"] == "Need_Attention"].index

new_df.to_csv("Need_Attention.csv")


############################################
# PROJE: RFM ile Müşteri Segmentasyonu
############################################
# Bir e-ticaret şirketi müşterilerini segmentlere ayırıp bu segmentlere göre pazarlama stratejileri belirlemek istiyor.
# online_retail_II.xlsx veri setinin "Year 2010-2011" isimli sheet'ine RFM analizi uygulayınız.

# Veri seti nerede? Aşağıdaki adreste yer alan "online_retail_II.xlsx" dosyasını indiriniz.
# https://www.kaggle.com/nathaniel/uci-online-retail-ii-data-set veya
# https://archive.ics.uci.edu/ml/machine-learning-databases/00502/

#############################################
# GÖREV 1: Derste ele alınan uygulamaların benzerlerini yapınız.
############################################

############################################
# GÖREV 2: Müşterileri segmentlere ayırdıktan sonra 3 segment seçerek bu 3 segmenti hem aksiyon
# kararları açısından hem de segmentlerin yapısı açısından (ortalama RFM değerleri açısından)
# yorumlayınız.
############################################

############################################
# GÖREV 3: "Loyal Customers" sınıfına ait customer ID'leri seçerek excel çıktısını alınız.
############################################

# RFM
# Recency afferim 5 puan gerçekten mantıklı bir 5 puan mı.
# sadakat programı : Need_Attention, At_Risk

# CLTV calculate
# CLTV prediction