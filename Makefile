TARGET := iphone:clang:latest:14.0
ARCHS = arm64

include $(THEOS)/makefiles/common.mk

# مكتبة مستقلة (dylib) بدون أي اعتماد على Substrate / ElleKit
LIBRARY_NAME = AflatoonSuite

AflatoonSuite_FILES = Tweak.xm
AflatoonSuite_CFLAGS = -fobjc-arc -Wno-deprecated-declarations
AflatoonSuite_FRAMEWORKS = UIKit Foundation QuartzCore AVFoundation AudioToolbox
AflatoonSuite_LOGOS_DEFAULT_GENERATOR = internal
AflatoonSuite_USE_SUBSTRATE = 0

# إصلاح خطأ الربط: "Shared cache eligible dylib cannot link to ineligible dylib CydiaSubstrate"
# 1) -not_for_dyld_shared_cache : يوقف فحص أهلية الـ shared cache الذي كان يُفشل الربط
# 2) -dead_strip_dylibs         : يحذف أي مكتبة مربوطة ولا يُستخدم منها شيء (Substrate)
AflatoonSuite_LDFLAGS += -Wl,-not_for_dyld_shared_cache -Wl,-dead_strip_dylibs

# NTgCalls (اختياري): لو وُضعت المكتبة داخل libs/ تُربط تلقائياً، وإلا يُبنى المشروع بدونها كالمعتاد.
# ضع libs/libntgcalls.a و libs/include/ntgcalls.h (من مخرجات build-ntgcalls-ios.yml).
# إن طلبت المكتبة أطر نظام إضافية وقت الربط، أضفها لسطر FRAMEWORKS أعلاه بحسب رسالة الخطأ.
ifneq ($(wildcard libs/libntgcalls.a),)
AflatoonSuite_CFLAGS += -DDS_HAS_NTGCALLS=1 -I$(CURDIR)/libs/include
AflatoonSuite_LDFLAGS += -L$(CURDIR)/libs -lntgcalls -lc++
endif

# VPN (اختياري): نواة Xray مبنية كمكتبة ثابتة (Go c-archive) عبر .github/workflows/build-xray-ios.yml
# ضع libs/libaflxray.a فتُربط تلقائياً ويُفعَّل زر VPN. بدونها يُبنى المشروع كالمعتاد ويُظهر الزر رسالة «النواة غير مرتبطة».
ifneq ($(wildcard libs/libaflxray.a),)
AflatoonSuite_CFLAGS += -DDS_HAS_XRAY=1
AflatoonSuite_LDFLAGS += -L$(CURDIR)/libs -laflxray -lresolv
AflatoonSuite_FRAMEWORKS += Security CoreFoundation
endif

# NetEQ (اختياري): neteq-rs مبنية كمكتبة ثابتة Rust عبر job «neteq» في .github/workflows/build-aflatoon.yml
# ضع libs/libaflneteq.a فتُربط تلقائياً ويُفعَّل زر NETEQ. بدونها يُبنى المشروع كالمعتاد ويُظهر الزر رسالة «غير مربوطة».
ifneq ($(wildcard libs/libaflneteq.a),)
AflatoonSuite_CFLAGS += -DDS_HAS_NETEQ=1 -I$(CURDIR)/neteq
AflatoonSuite_LDFLAGS += -L$(CURDIR)/libs -laflneteq
endif

include $(THEOS_MAKE_PATH)/library.mk
