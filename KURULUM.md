# Arda Research — GitHub için tam kaynak paketi

ABD, kripto ve BIST araştırma sitesi. Mevcut yayımlanmış 20. sürümün tüm kaynak kodu ve derlenmiş uygulaması dahildir: 107 ABD şirketi, 500 kripto ve 500 BIST kaydı. Her varlıkta aynı miktarda doğrulanmış bilgi olduğu anlamına gelmez; eksikler arayüzde belirtilir.

## GitHub'a yükle

1. ZIP'i bilgisayarında aç.
2. GitHub'da repository oluştur. Araştırma veri dökümleri de bulunduğu için başlangıçta **Private** seç.
3. **Add file → Upload files** ile klasörün **içindekileri** yükle. README.md ve package.json kökte olsun. ZIP'i tek dosya olarak yüklemek siteyi kurmaz.
4. Büyük yüklemelerde terminal ile `git init`, `git add .`, `git commit -m "Initial export"` ve GitHub'ın verdiği uzak repository/push komutlarını kullan.

## Paket içeriği

- `web/`: ABD–kripto–BIST ekranları, portföy arayüzleri, şirket dosyaları ve stiller.
- `worker/`: API'ler, özel portföy işlemleri, bülten, teknik hesap motoru ve veri adaptörleri.
- `data/`: kayıtlı araştırma girdileri ve veri görüntüleri.
- `dist/server/index.js`: mevcut yayının derlenmiş uygulaması; servis edilen ekranlar bu Worker içine gömülüdür.
- `scripts/`: derleme, doğrulama ve tarihî araştırma hazırlama araçları.
- `DAILY-UPDATES.md`: veri bağlantıları ve günlük yenileme protokolü.
- `deployment/cloudflare-public.js`: ayrı Cloudflare yayını için halka açık okuma adaptörü.

## Derleme

Node.js 20+ (24 ile doğrulandı), Python 3.12+ ve bash gerekir. Ana derleme için ek JavaScript paketi indirmek gerekmez.

```bash
npm run build
npm run validate
```

Güncel giriş noktası `scripts/build.sh` dosyasıdır. Ana derleme kendi `data/build-home-baseline.html` girdisini kullanır; eski Git commitlerine ihtiyaç duymaz. Diğer tarihî araştırma scriptleri haricî ham veri/önceki commitler isteyebilir; normal kurulumda bunları çalıştırma. Mevcut raporları topluca yeniden üretmek için yazılmamışlardır.

## GitHub Pages ile sunucu arasındaki fark

**GitHub bir kod deposudur. GitHub Pages tam uygulamanın backend'ini çalıştırmaz.** Yalnız dosyaları yüklemek, Pages'i açmak veya HTML'yi çift tıklamak portföy API'sini ve günlük yenilemeyi çalıştırmaz.

Mevcut Sites yayını Worker, R2 depolama ve ChatGPT giriş sistemini kullanır. `.openai/hosting.json` orijinal site kimliğini korur; yeni hosting hesabı oluşturmaz. Bu dışa aktarım mevcut siteyi değiştirmez.

### Ayrı Cloudflare üzerinde halka açık araştırma ekranları

1. Hesabında `arda-research-data` adlı R2 bucket oluştur veya örnekteki adı kendi bucket adına göre değiştir.
2. `wrangler.example.jsonc` dosyasını `wrangler.jsonc` olarak kopyala.
3. Wrangler girişini/hesap bağlantısını tamamladıktan sonra:

```bash
npm run build
npx wrangler dev --config wrangler.jsonc
# İnceleme ve hosting ayarlarından sonra:
npx wrangler deploy --config wrangler.jsonc
```

Bu teslimatta gerçek dış hosting yayını denenmedi. Servis ücretleri/kotaları hesabının planına bağlıdır; paket ücretli servis, alan adı veya hesap oluşturmaz.

### Giriş ve özel portföyler

Sites sürümü, platformun doğruladığı `oai-authenticated-user-*` başlıklarından kullanıcı kimliği alır. Bunlara bağımsız bir origin üzerinde doğrudan güvenilemez. Cloudflare adaptörü tüm `oai-*` başlıklarını siler; bu nedenle **haricî yayında hesaba bağlı portföy API'leri erişime kapalıdır ve Sites'a özgü giriş düğmesi çalışmaz**. Tam bağımsız kullanım için geliştiricinin OAuth/oturum doğrulamasını ve giriş ekranlarını uyarlaması gerekir. Tüm portföy kaynak kodu pakettedir; hazır bağımsız kullanıcı hesabı hizmeti iddia edilmez. Orijinal Worker dosyasını doğrulanmamış kimlik başlıklarına açık bir origin üzerinde doğrudan yayımlama.

Özel portföy kayıtları, işlem geçmişi, kullanıcı oturumları, servis anahtarları ve R2 içeriği pakete dahil değildir. Kod dışa aktarımı kullanıcı verisini taşımaz.

### Fiyat ve veri yenileme

Güncel fiyatlar TradingView'in resmî gömme panellerinden gelir; internet/sağlayıcı erişimi gerekir. Bülten API'si resmî RSS kaynaklarını tarar, R2'ye kaydeder. ABD/BIST günlük teknik hesapları uygun EODHD bağlantısı ve gösterim yetkisi; kripto için desteklenen geçmiş veri bağlantısı gerektirir. Bu kaynak sürümünde geçmiş veri bağlantıları yapılandırılmamıştı. Eski analiz tarihleri günlük fiyat gibi değiştirilmez. Güncel CMC sıralaması/her varlıkta tam geçmiş veri garantisi yoktur.

Gerçek anahtarları yalnız hosting secrets bölümüne gir; GitHub'a yükleme. `.dev.vars.example` boş örnektir. Sites zamanlanmış görevleri yeni repository/hostinge otomatik taşınmaz; protokol `DAILY-UPDATES.md` içindedir. İsteğe bağlı OpenAI portföy analizi ayrıca sunucu anahtarı ve kullanıcı isteği gerektirir; kullanım ücreti ilgili hesaba bağlıdır.

## Kontroller ve sınırlar

Git geçmişi olmayan temiz klasörde ana derleme ve ESM doğrulaması yapılmıştır. Paketlenen uygulamanın temel sayfaları/API'leri ve haricî adaptörde anonim/kimlik başlığı erişim sınırı kontrol edilmiştir. Test fixture'ları gerçek piyasa yenilemesi değildir. Görsel tarayıcı ve bağımsız hosting giriş bağlantısı doğrulanmadı.

`EXPORT-MANIFEST.json` kaynak commitini ve dosya SHA-256 değerlerini içerir. Sağlayıcı kaynaklı araştırma dökümlerinin açık repository'de yeniden dağıtım haklarını ayrıca değerlendir.
