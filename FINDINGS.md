# هندسة عكسية: AgoraRtcKit 3.7.3.188 (من Yalla_Ludo-4_6_0.ipa) — arm64

الأدوات: `xref.py` (يجد مراجع ADRP+ADD للنصوص ويربطها بالدوال عبر LC_FUNCTION_STARTS)، `dis.py` (مفكّك ARM64 مصغّر جزئي — ليس كاملاً).
العناوين = إزاحة الملف (قطعة __TEXT تبدأ من 0).

## ما وُجد (محقق من الثنائي)
| العنوان | الدور |
|---|---|
| 0x49f1c0 | سجل المعاملات: يسجّل كل مفاتيح `che.audio.neteq.*` (مفتاح ← خانة بقيمة افتراضية ونوع) |
| 0x51daec | `NetEq initialize`: يطبع/يستهلك إعدادات accelerate_opt و target_level_improve |
| 0x4931bc / 0x493434 | SetNetEQPlayoutMode / SetNetEQAccelerateOpt |
| 0x4933b0 / 0x49332c | SetNetEQMinimumPlayoutDelay / SetNetEQMaximumPlayoutDelay |
| 0x2fb29c / 0x2fb428 / 0x2fb52c | واجهات min playout delay (عامة/متحدث/جمهور) وفيها سقف 4 ثوانٍ |
| 0x4d6aac | "More than 20 small ts frames arrived, flush neteq buffer" |

الـ SDK يملك `getParameter:args:` و`getParameters:` — استُخدما لإضافة قراءة راجعة (Readback) في التويك.

## ما لم يُنجَز (بصراحة)
- لم أستخرج القيم الافتراضية ولا حدود القص لكل معامل: الدوال مقسّمة (outlined) وحدود LC_FUNCTION_STARTS لا تكفي،
  والمفكّك المصغّر لا يغطي كل التعليمات، ولا أملك جهازاً ولا محاكياً للتحقق.
- **لا يوجد ترقيع (patch) للثنائي في هذا المشروع**: ترقيع بلا اختبار على جهاز قد يعطّل الصوت أو يسقط التطبيق، وترقيع __TEXT وقت التشغيل
  غير ممكن عادةً في تطبيق مُعاد توقيعه (حماية W^X). الترقيع الممكن فقط على الملف قبل إعادة التوقيع.

## الخطوة العملية التالية
شغّل اللعبة بمستوى 3 أو 4، ثم اقرأ `Documents/AflatoonSuite/agora_readback.txt`: القيم التي رجعت كما أُرسلت مقبولة،
والفارغة أو المختلفة مرفوضة/مقصوصة — وهذا يحدد أين يستحق الحفر أكثر في الثنائي.
