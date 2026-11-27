# دمج NetEQ (neteq-rs) في AflatoonSuite

## ما الذي أُضيف
- `neteq/` : غلاف C ABI بلغة Rust فوق `neteq-core` (نسخة مضمّنة) → يُبنى `libaflneteq.a` لـ `aarch64-apple-ios`.
- `neteq/aflneteq.h` : الواجهة (`afl_neteq_new / process / reset / free`).
- `Tweak.xm` : مرحلة NetEQ لكل متكلم (uid) داخل `onPlaybackAudioFrameBeforeMixing`، قبل محركات السرعة.
  زر جديد `NETEQ: ON/OFF` بجانب VOICE SPEED (يُحفظ في الإعدادات باسم `netEqOn`).
- `Makefile` : يربط `libs/libaflneteq.a` تلقائياً إن وُجدت (`-DDS_HAS_NETEQ=1`) وإلا يُبنى كالمعتاد.
- `.github/workflows/build-aflatoon.yml` : job جديد `neteq` يبني مكتبة Rust ثم يمرّرها لـ job البناء.

## ماذا يفعل فعلياً (وما لا يفعله)
Agora يطبّق NetEQ الخاص به داخل الـ SDK قبل أن يصل الصوت للتويك، والتويك يرى PCM مفكوك فقط.
لذلك هذه المرحلة **لا تستبدل** مخزن Agora، بل تضيف فوقه:
- **PLC**: بعد كلام، إذا وصلت فريمات صمت تام (حتى 3 × 10ms) تُعامل كفقدان وتُملأ بامتداد نغمة الصوت بدل الانقطاع.
- **Merge**: دمج سلس (crossfade) عند رجوع الصوت.
- **Comfort noise** عند الفقدان الطويل.
الإعداد الحالي `min=1, max=2` فريم = **بدون تأخير إضافي** (لا تمدد ولا تسريع من NetEQ؛ التسريع يبقى لمحركات السرعة الموجودة).
لو رفعت `afl_neteq_new(sr, 1, 2)` إلى max أكبر في `Tweak.xm` يبدأ NetEQ بالتمدد/التسريع لكن يزيد التأخير.

## البناء
شغّل workflow `Build AflatoonSuite` (workflow_dispatch). ابحث في السجل عن `afl_neteq_` في خطوة «Check Xray is linked».
