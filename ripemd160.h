#ifndef __RIPEMD160_H__
#define __RIPEMD160_H__

#include <stdint.h>

typedef struct _RIPEMD160_CTX {
    uint32_t total[2];    /*!< number of bytes processed  */
    uint32_t state[5];    /*!< intermediate digest state  */
    uint8_t buffer[64];   /*!< data block being processed */
} RIPEMD160_CTX;

void ripemd160_Init(RIPEMD160_CTX *ctx);
void ripemd160_Update(RIPEMD160_CTX *ctx, const uint8_t *input, uint32_t ilen);
void ripemd160_Final(uint8_t output[20], RIPEMD160_CTX *ctx);
void ripemd160(const uint8_t *msg, uint32_t msg_len, uint8_t hash[20]);

#endif
