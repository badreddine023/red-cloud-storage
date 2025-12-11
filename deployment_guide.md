# دليل نشر "ضبابة الحمراء" (Red Cloud) - تخزين سحابي ذاتي الاستضافة

هذا الدليل يوضح كيفية نشر حل التخزين السحابي المتوافق مع S3 (MinIO) باستخدام Docker Compose وعكس وكيل (Reverse Proxy) Caddy لتوفير شهادات TLS مجانية وتلقائية (HTTPS).

**الاسم المقترح للمشروع:** ضبابة الحمراء (Red Cloud)
**المكونات:** MinIO (تخزين S3)، Caddy (TLS و Reverse Proxy)، Docker Compose.

---

## 1. المتطلبات الأساسية

لنجاح عملية النشر، يجب توفير ما يلي:

1.  **خادم افتراضي خاص (VPS):** يعمل بنظام Linux (مثل Ubuntu) مع وصول إلى الجذر (Root Access).
2.  **اسم نطاق (Domain Name):** يجب أن يكون لديك نطاق (Domain) فرعي موجه إلى عنوان IP الخاص بالـ VPS.
    *   **مثال:** `storage.yourdomain.com` (هذا ما يجب استبداله في ملف `Caddyfile`).
3.  **Docker و Docker Compose:** يجب تثبيتهما على الـ VPS.

## 2. ملفات الإعداد

يجب إنشاء مجلد للمشروع (مثلاً: `red_cloud_storage`) ووضع الملفات التالية بداخله.

### أ. ملف `docker-compose.yml`

هذا الملف يقوم بتشغيل حاوية MinIO وحاوية Caddy وربطهما بشبكة داخلية.

```yaml
version: "3.8"

services:
  minio:
    image: minio/minio:latest
    container_name: red_cloud_minio
    restart: unless-stopped
    environment:
      # **مهم جداً: قم بتغيير هذه القيم إلى كلمات سر قوية وآمنة**
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: VeryStrongPassword123!
    volumes:
      # مجلد تخزين بيانات MinIO الدائم
      - ./minio_data:/data
    command: server /data --console-address ":9001"
    networks:
      - web

  caddy:
    image: caddy:2
    container_name: red_cloud_caddy
    restart: unless-stopped
    ports:
      # Caddy يستمع على المنافذ القياسية لـ HTTP و HTTPS
      - "80:80"
      - "443:443"
    volumes:
      # ملف إعداد Caddyfile
      - ./Caddyfile:/etc/caddy/Caddyfile
      # مجلد بيانات Caddy لتخزين شهادات TLS (Let's Encrypt)
      - caddy_data:/data
      - caddy_config:/config
    networks:
      - web

networks:
  web:
    driver: bridge

volumes:
  caddy_data:
  caddy_config:
```

### ب. ملف `Caddyfile`

هذا الملف يوجه حركة المرور من اسم النطاق الخاص بك إلى حاوية MinIO، ويقوم Caddy تلقائياً بتوفير شهادة SSL/TLS.

```caddy
# **مهم جداً: استبدل 'storage.example.com' باسم النطاق الفعلي الخاص بك**
storage.example.com {
    # توجيه الطلبات إلى حاوية MinIO على المنفذ الداخلي 9000
    reverse_proxy minio:9000
}

# يمكنك إضافة نطاق فرعي آخر لواجهة التحكم (Console) إذا أردت:
# console.example.com {
#     reverse_proxy minio:9001
# }
```

## 3. خطوات النشر (على الـ VPS)

1.  **تسجيل الدخول وإنشاء المجلد:**
    ```bash
    ssh user@your_vps_ip
    mkdir -p red_cloud_storage/minio_data
    cd red_cloud_storage
    ```

2.  **إنشاء الملفات:**
    *   استخدم محرر نصوص (مثل `nano` أو `vim`) لإنشاء ملف `docker-compose.yml` و `Caddyfile` بالبيانات المذكورة أعلاه، مع التأكد من استبدال `storage.example.com` باسم النطاق الخاص بك.

3.  **تشغيل الخدمات:**
    ```bash
    sudo docker compose up -d
    ```
    سيقوم هذا الأمر بسحب صور Docker وتشغيل MinIO و Caddy في الخلفية.

4.  **التحقق من التشغيل:**
    ```bash
    sudo docker compose ps
    ```
    يجب أن ترى حاويتي `red_cloud_minio` و `red_cloud_caddy` بحالة `Up`.

## 4. الوصول والاستخدام

بمجرد تشغيل الخدمات، يمكنك الوصول إلى التخزين السحابي الخاص بك:

1.  **واجهة التحكم (Console):**
    *   اذهب إلى `https://storage.yourdomain.com:9001` (إذا لم تستخدم Caddy لواجهة التحكم) أو `https://console.yourdomain.com` (إذا أضفت إعداد Caddy الاختياري).
    *   استخدم بيانات الاعتماد: **User:** `minioadmin`، **Password:** `VeryStrongPassword123!` (التي يجب أن تكون قد غيرتها).

2.  **الوصول البرمجي (S3 API):**
    *   نقطة النهاية (Endpoint) هي: `https://storage.yourdomain.com`
    *   يمكنك استخدام أي أداة متوافقة مع S3 مثل `awscli` أو `boto3` (Python) للتفاعل مع التخزين الخاص بك.

### مثال استخدام Python (يتطلب تثبيت `boto3`)

قم بتثبيت المكتبة: `pip install boto3`

استخدم الكود التالي (ملف `minio_python_example.py`) للتفاعل مع التخزين، مع استبدال القيم بالدومين وكلمة السر الخاصة بك:

```python
import boto3
from botocore.client import Config

# **مهم: استبدل القيم هنا**
MINIO_ENDPOINT = 'https://storage.yourdomain.com'
ACCESS_KEY = 'minioadmin'
SECRET_KEY = 'VeryStrongPassword123!'
BUCKET_NAME = 'red-cloud-bucket'
FILE_TO_UPLOAD = 'test_file.txt'

# تهيئة عميل S3
s3 = boto3.client(
    's3',
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    config=Config(signature_version='s3v4'),
    region_name='us-east-1'
)

try:
    # إنشاء Bucket
    s3.create_bucket(Bucket=BUCKET_NAME)
    print(f"Bucket '{BUCKET_NAME}' created successfully.")

    # رفع ملف
    # (يجب أن يكون لديك ملف اسمه 'test_file.txt' في نفس المجلد)
    s3.upload_file(FILE_TO_UPLOAD, BUCKET_NAME, FILE_TO_UPLOAD)
    print(f"File '{FILE_TO_UPLOAD}' uploaded successfully.")

    # قائمة الملفات
    response = s3.list_objects_v2(Bucket=BUCKET_NAME)
    print("Objects in bucket:")
    for obj in response.get('Contents', []):
        print(f"- {obj['Key']}")

except Exception as e:
    print(f"An error occurred: {e}")
```

---

**ملاحظة هامة:** فشلت محاولات تشغيل Docker Compose محلياً في بيئة Sandbox بسبب قيود الشبكة والـ `iptables`. لذلك، تم تزويدك بالملفات الصحيحة والخطوات المفصلة لتطبيق الحل مباشرة على **VPS حقيقي**، حيث ستعمل هذه الإعدادات بشكل صحيح.

بالتوفيق في نشر "ضبابة الحمراء"!
