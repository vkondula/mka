# coding=utf-8

#MKA:xkondu00
# ------------ RULES ONLY ------------ 
[start_1]
start_1 = !SPACE
state = !ALPHA
	current

[state]
state = !ALPHANUM
	current
state_body = _
	current
left_ap = '
pre_apost = !SPACE

[state_body]
state = !ALPHANUM
	current
state_body = _
	current

[pre_apost]
pre_apost = !SPACE
left_ap = '

[left_ap]
apost2 = '
	input
symbol = !NOTAPOST
	input

[apost2]
right_ap = !SPACE
dash = -
symbol = '
	input

[symbol]
right_ap = '

[right_ap]
right_ap = !SPACE
dash = -

[dash]
arrow = >

[arrow]
arrow = !SPACE
target = !ALPHA
	target

[target.]
target = !ALPHANUM
	target
target_body = _
	target
comma = ,
	finish
pre_comma = !SPACE
	finish
pre_comma_4 = .
	finish

[target_body]
target = !ALPHANUM
	target
target_body = _
	target

[pre_comma.]
pre_comma = !SPACE
comma = ,

[pre_comma_4.]
pre_comma_4 = !SPACE
comma = ,

[comma.]
comma = !SPACE
state = !ALPHA
	current
