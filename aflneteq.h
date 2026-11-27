#ifndef AFLNETEQ_H
#define AFLNETEQ_H
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
typedef struct AflNetEq AflNetEq;
AflNetEq *afl_neteq_new(int sample_rate, int min_delay_frames, int max_delay_frames);
int  afl_neteq_process(AflNetEq *h, const int16_t *in, int16_t *out, int n, int lost);
void afl_neteq_reset(AflNetEq *h);
void afl_neteq_free(AflNetEq *h);
#ifdef __cplusplus
}
#endif
#endif
