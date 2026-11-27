# طريقة البناء على GitHub (من الصفر إلى الـ dylib)

1. أنشئ مستودعاً جديداً على GitHub (يمكن أن يكون Private).
2. ارفع **محتويات** هذا المجلد إلى جذر المستودع (يجب أن يظهر `Tweak.xm` و`Makefile` و`.github` مباشرة في الصفحة الرئيسية للمستودع).
   - من الموقع: Add file ← Upload files، واسحب كل الملفات والمجلدات (ومنها المجلد المخفي `.github`).
   - إن لم يظهر `.github` عند السحب، أنشئ الملف يدوياً: Add file ← Create new file واكتب المسار `.github/workflows/build-aflatoon.yml` والصق محتواه.
3. افتح تبويب **Actions**. إن ظهر زر تفعيل الـ workflows فاضغطه.
4. اختر **Build AflatoonSuite (with Xray VPN core)** ← **Run workflow**.
5. انتظر (حوالي 10 إلى 20 دقيقة). بعد النجاح انزل لقسم **Artifacts** ونزّل `AflatoonSuite`.
6. داخله `AflatoonSuite.dylib`. احقنه في الـ IPA بـ Sideloadly أو ESign أو Feather.

إن فشل بناء Xray بالإصدار latest: أعد التشغيل واكتب `v25.3.6` في خانة الإصدار.
إن فشل أي خطوة: انسخ نص الخطأ من سجل الخطوة الحمراء وأرسله.
