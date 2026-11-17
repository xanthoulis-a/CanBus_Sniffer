/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file    fdcan.h
  * @brief   This file contains all the function prototypes for
  *          the fdcan.c file
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2025 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __FDCAN_H__
#define __FDCAN_H__

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "main.h"

/* USER CODE BEGIN Includes */
#define FDCANQUEUE_SIZE 64
/* USER CODE END Includes */

typedef struct {
    uint32_t ID;
    uint8_t DLC;
    uint8_t Data[8];
} RxFDCANmessage;

extern FDCAN_HandleTypeDef hfdcan1;

extern FDCAN_HandleTypeDef hfdcan2;

/* USER CODE BEGIN Private defines */
extern volatile uint8_t UARTbusy;

extern RxFDCANmessage FDCANqueue1[ FDCANQUEUE_SIZE ];
extern volatile uint8_t FDCAN1queue_inserted;
extern volatile uint8_t FDCAN1queue_forwarded;

extern RxFDCANmessage FDCANqueue2[ FDCANQUEUE_SIZE ];
extern volatile uint8_t FDCAN2queue_inserted;
extern volatile uint8_t FDCAN2queue_forwarded;

// struct RxFDCANmessage *tempqueue;
//uint8_t *temp_insert;
//uint8_t *temp_forward;



/* USER CODE END Private defines */

void MX_FDCAN1_Init(void);
void MX_FDCAN2_Init(void);

/* USER CODE BEGIN Prototypes */

//void FDCAN2UART_Transmit( struct RxFDCANmessage *tempqueue , uint8_t *temp_insert , uint8_t *temp_forward);
void FDCAN2UARTTransmit(FDCAN_HandleTypeDef *fdcanHandle);

/* USER CODE END Prototypes */

#ifdef __cplusplus
}
#endif

#endif /* __FDCAN_H__ */

