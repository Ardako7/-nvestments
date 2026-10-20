# Arda Research — az dosyalı GitHub paketi

Bu paket GitHub'ın tek yüklemede 100 dosya sınırına uygun hazırlanmıştır. ZIP'i aç ve içindeki dosya/klasörleri GitHub repository köküne yükle. ZIP dosyasını tek başına yüklemek siteyi kurmaz.

## İçerik

- `dist/server/index.js`: tüm ABD, kripto, BIST, şirket ve portföy ekranları ile backend'i içeren derlenmiş uygulama.
- `deployment/cloudflare-public.js`: bağımsız Cloudflare yayını için halka açık adaptör.
- `wrangler.example.jsonc`: hosting ve R2 bağlantısı örneği.
- `KURULUM.md`: tam kurulum, veri ve bağımsız kullanıcı girişi gereksinimleri.
- `TAM-KAYNAK-KODU.zip`: orijinal 283 dosyalık düzenlenebilir kaynak paketi. Kaynaklar eksiltilmedi; yalnız bu arşive taşındı. Uygulamayı mevcut haliyle yayımlamak için bu iç ZIP'i açmak gerekmez. Geliştirme yapmak için bilgisayarında ayrı bir klasöre aç ve içindeki README'yi izle.

## Hazır uygulamayı doğrulama

Node.js 20+ gerekir:

```bash
npm run validate
```

Hazır Worker için yeniden derleme gerekmez. Kaynak değişikliği yapacaksan `TAM-KAYNAK-KODU.zip` içindeki tam projeyi kullan.

## Yayın

GitHub Pages bu backend'i çalıştırmaz. Ayrı Cloudflare hesabında R2 bucket oluşturup `wrangler.example.jsonc` dosyasını `wrangler.jsonc` olarak kopyaladıktan sonra:

```bash
npx wrangler dev --config wrangler.jsonc
# Kontrol ve hesap yapılandırmasından sonra:
npx wrangler deploy --config wrangler.jsonc
```

**Bağımsız özel portföy girişi ayrıca uyarlanmalıdır.** Sites'a özel giriş dış hostinge otomatik taşınmaz. Sağlanan adaptör, doğrulanmamış kimlik başlıklarını siler ve hesap portföylerine erişimi kapalı tutar. Kaynak kodu eksiksizdir; kullanıcı verileri, gizli anahtarlar ve mevcut sunucu depolaması dahil değildir. Günlük teknik veri bağlantıları ayrıca gerekir. Ayrıntılar `KURULUM.md` içinde.

İlk repository'yi Private oluştur. `TAM-KAYNAK-KODU.zip` içindeki 283 dosyayı web arayüzünde tek seferde açıp yüklemeye çalışma; düzenlenebilir dosyaları ayrı ayrı tutmak istersen Git ile push veya 100'den küçük yükleme partileri kullan.
