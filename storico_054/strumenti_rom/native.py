"""Small thumb routines called with `callnative` from scripts."""

SRC = r'''
	.align 2
	.thumb_func
	.global R22_ShinyCore
R22_ShinyCore:
	push {r4-r7,lr}
	sub sp, #16
	mov r4, r0
	mov r5, r1
	mov r6, r2
	ldr r3, =0x0806f489
	bl R22_CallR3
	lsl r0, r0, #16
	lsr r7, r0, #16
	ldr r1, =0x03005d90
	ldr r1, [r1]
	ldrb r2, [r1, #10]
	ldrb r3, [r1, #11]
	lsl r3, r3, #8
	orr r2, r3
	ldrb r3, [r1, #12]
	eor r2, r3
	ldrb r3, [r1, #13]
	lsl r3, r3, #8
	eor r2, r3
	eor r2, r7
	lsl r2, r2, #16
	orr r7, r2
	mov r0, #1
	str r0, [sp, #0]
	str r7, [sp, #4]
	mov r0, #0
	str r0, [sp, #8]
	str r0, [sp, #12]
	mov r0, r4
	mov r1, r5
	mov r2, r6
	mov r3, #32
	ldr r7, =0x08067a09
	bl R22_CallR7
	add sp, #16
	pop {r4-r7}
	pop {r0}
	bx r0

	.align 2
	.thumb_func
	.global R22_ShinyWild
R22_ShinyWild:
	push {lr}
	ldr r0, =0x02024744
	ldr r3, =0x020375e0
	ldrh r1, [r3]
	ldrh r2, [r3, #2]
	bl R22_ShinyCore
	pop {r0}
	bx r0

	.align 2
	.thumb_func
	.global R22_ShinyGift
R22_ShinyGift:
	push {r4,lr}
	sub sp, #100
	mov r0, sp
	ldr r3, =0x020375e0
	ldrh r1, [r3]
	ldrh r2, [r3, #2]
	bl R22_ShinyCore
	mov r0, sp
	ldr r3, =0x0806b2d1
	bl R22_CallR3
	ldr r3, =0x020375f0
	strh r0, [r3]
	ldr r3, =0x020375e0
	ldrh r4, [r3, #4]
	mov r0, r4
	mov r1, #2
	ldr r3, =0x080c0849
	bl R22_CallR3
	mov r0, r4
	mov r1, #3
	ldr r3, =0x080c0849
	bl R22_CallR3
	add sp, #100
	pop {r4}
	pop {r0}
	bx r0

	.thumb_func
R22_CallR3:
	bx r3
	.thumb_func
R22_CallR7:
	bx r7
	.ltorg
	.align 2
'''
