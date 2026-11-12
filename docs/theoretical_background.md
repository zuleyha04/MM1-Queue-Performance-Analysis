
# M/M/1 Kuyruk Modelinin Teorik Analizi

## 1. Modelin Tanımı

Bu çalışmada, bir ağ yönlendiricisine ulaşan paketlerin
bekleme ve işlenme süreçleri M/M/1 kuyruk modeli ile
incelenmektedir.

M/M/1 modelinde paket gelişleri Poisson süreci ile
modellenirken paketler arası geliş süreleri ve servis
süreleri üstel dağılıma sahiptir. Sistemde tek bir
sunucu bulunmaktadır.

Modelde FIFO servis disiplini, sınırsız kuyruk kapasitesi
ve bağımsız geliş ve servis süreçleri varsayılmaktadır.

## 2. Model Parametreleri

- λ: Ortalama paket geliş hızı (paket/sn)
- μ: Ortalama servis hızı (paket/sn)
- ρ = λ/μ: Trafik yoğunluğu

Kararlı durumun sağlanması için 0 ≤ λ < μ ve μ > 0
koşulları gereklidir.

## 3. Kararlı Durum Olasılıkları

M/M/1 modelinde denge denklemleri:

λP_n = μP_(n+1)

Buradan:

P_n = ρ^n P_0

Olasılıkların toplamının 1 olması koşuluyla:

P_0 = 1 - ρ

Dolayısıyla:

P_n = (1 - ρ)ρ^n

## 4. Sistemdeki Ortalama Paket Sayısı

L = Σ(n × P_n), n = 0,...,∞

Geometrik seri özdeşliği kullanılarak:

L = ρ / (1 - ρ)

## 5. Kuyruktaki Ortalama Paket Sayısı

Sunucunun meşgul olma olasılığı ρ olduğundan:

Lq = L - ρ

Lq = ρ² / (1 - ρ)

## 6. Ortalama Sistemde Kalış Süresi

Little Kanunu:

L = λW

λ > 0 için:

W = L / λ

Sonuç:

W = 1 / (μ - λ)

## 7. Ortalama Kuyrukta Bekleme Süresi

Ortalama servis süresi 1/μ olduğundan:

Wq = W - 1/μ

Wq = λ / [μ(μ - λ)]

## 8. Little Kanunu'nun Doğrulanması

L = λW

Lq = λWq

Örnek olarak λ = 5 ve μ = 10 için:

ρ = 0.5
L = 1 paket
Lq = 0.5 paket
W = 0.2 saniye
Wq = 0.1 saniye

L = 5 × 0.2 = 1

Lq = 5 × 0.1 = 0.5

Her iki eşitlik de sağlanmaktadır.

## 9. Kararlı Durumun Sınırları

Trafik yoğunluğu 1'e yaklaştıkça ortalama kuyruk
uzunluğu ve bekleme süresi hızla artmaktadır.

ρ ≥ 1 durumunda standart sınırsız kapasiteli M/M/1
modelinin sonlu ortalamalara sahip kararlı durum
çözümü bulunmamaktadır.
