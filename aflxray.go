// Aflatoon Suite — غلاف C بسيط حول xray-core (يُبنى كمكتبة ثابتة c-archive لـ iOS).
// الواجهة (C ABI) يستعملها Tweak.xm:
//   char *AflXrayStart(char *configJSON);  // nil عند النجاح، وإلا نص الخطأ (يُحرَّر بـ AflXrayFree)
//   void  AflXrayStop(void);
//   char *AflXrayVersion(void);            // يُحرَّر بـ AflXrayFree
//   void  AflXrayFree(char *p);
package main

/*
#include <stdlib.h>
*/
import "C"

import (
	"bytes"
	"runtime/debug"
	"sync"
	"unsafe"

	"github.com/xtls/xray-core/core"
	"github.com/xtls/xray-core/infra/conf/serial"
	_ "github.com/xtls/xray-core/main/distro/all" // يسجّل كل البروتوكولات والنقل (vless/vmess/trojan/ss، ws/grpc/xhttp، tls/reality)
)

var (
	mu       sync.Mutex
	instance *core.Instance
)

func init() {
	// النواة تعيش داخل تطبيق/لعبة: نقلّل استهلاك الذاكرة قدر الإمكان
	debug.SetGCPercent(50)
	debug.SetMemoryLimit(96 << 20)
}

//export AflXrayStart
func AflXrayStart(cfg *C.char) *C.char {
	mu.Lock()
	defer mu.Unlock()
	if instance != nil {
		_ = instance.Close()
		instance = nil
	}
	conf, err := serial.LoadJSONConfig(bytes.NewReader([]byte(C.GoString(cfg))))
	if err != nil {
		return C.CString("config: " + err.Error())
	}
	inst, err := core.New(conf)
	if err != nil {
		return C.CString("new: " + err.Error())
	}
	if err := inst.Start(); err != nil {
		_ = inst.Close()
		return C.CString("start: " + err.Error())
	}
	instance = inst
	return nil
}

//export AflXrayStop
func AflXrayStop() {
	mu.Lock()
	defer mu.Unlock()
	if instance != nil {
		_ = instance.Close()
		instance = nil
	}
	debug.FreeOSMemory()
}

//export AflXrayVersion
func AflXrayVersion() *C.char { return C.CString(core.Version()) }

//export AflXrayFree
func AflXrayFree(p *C.char) {
	if p != nil {
		C.free(unsafe.Pointer(p))
	}
}

func main() {}
