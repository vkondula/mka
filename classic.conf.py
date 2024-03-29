# coding=utf-8

#MKA:xkondu00
# ------------ READ STATES ------------

[start_1]
start_1 = !SPACE
left_1 = (

[left_1]
left_1 = !SPACE
opening_1 = {

[opening_1]
start_2 = }
opening_1 = !SPACE
state_1 = !ALPHA
	state

[state_1]
state_1 = !ALPHANUM
	state
state_body_1 = _
	state
comma_1 = ,
pre_comma_1 = !SPACE
start_2 = }

[state_body_1]
state_1 = !ALPHANUM
	state
state_body_1 = _
	state

[pre_comma_1]
pre_comma_1 = !SPACE
comma_1 = ,
start_2 = }

[comma_1]
comma_1 = !SPACE
state_1 = !ALPHA
	state


# ------------ READ ALPHABET ------------

[start_2]
start_2 = !SPACE
start_comma_2 = ,

[start_comma_2]
left_2 = {
start_comma_2 = !SPACE

[left_2]
start_3 = }
left_2 = !SPACE
left_ap_2 = '

[left_ap_2]
apost2_2 = '
	symbol
symbol_2 = !NOTAPOST
	symbol

[apost2_2]
symbol_2 = '
	symbol

[symbol_2]
right_ap_2 = '

[right_ap_2]
right_ap_2 = !SPACE
comma_2 = ,
start_3 = }

[comma_2]
comma_2 = !SPACE
left_ap_2 = '


# ------------ READ RULES ------------

[start_3]
start_3 = !SPACE
start_comma_3 = ,

[start_comma_3]
left_3 = {
start_comma_3 = !SPACE

[left_3]
start_4 = }
left_3 = !SPACE
state_3 = !ALPHA
	current

[state_3]
state_3 = !ALPHANUM
	current
state_body_3 = _
	current
left_ap_3 = '
pre_apost_3 = !SPACE
start_4 = }

[state_body_3]
state_3 = !ALPHANUM
	current
state_body_3 = _
	current

[pre_apost_3]
pre_apost_3 = !SPACE
left_ap_3 = '

[left_ap_3]
apost2_3 = '
	input
symbol_3 = !NOTAPOST
	input

[apost2_3]
right_ap_3 = !SPACE
dash_3 = -
symbol_3 = '
	input

[symbol_3]
right_ap_3 = '

[right_ap_3]
right_ap_3 = !SPACE
dash_3 = -

[dash_3]
arrow_3 = >

[arrow_3]
arrow_3 = !SPACE
target_3 = !ALPHA
	target

[target_3]
target_3 = !ALPHANUM
	target
target_body_3 = _
	target
comma_3 = ,
pre_comma_3 = !SPACE
start_4 = }

[target_body_3]
target_3 = !ALPHANUM
	target
target_body_3 = _
	target

[pre_comma_3]
pre_comma_3 = !SPACE
comma_3 = ,
start_4 = }

[comma_3]
comma_3 = !SPACE
state_3 = !ALPHA
	current

# ------------ READ STARTING ------------

[start_4]
start_4 = !SPACE
start_comma_4 = ,

[start_comma_4]
start_comma_4 = !SPACE
start_state_4 = !ALPHA
	start

[start_state_4]
start_state_4 = !ALPHANUM
	start
start_body_4 = _
	start
pre_second_comma_4 = !SPACE
second_comma_4 = ,

[start_body_4]
start_body_4 = _
	start
start_state_4 = !ALPHANUM
	start


[pre_second_comma_4]
pre_second_comma_4 = !SPACE
second_comma_4 = ,

# ------------ READ FINISHING ------------

[second_comma_4]
second_comma_4 = !SPACE
opening_4 = {

[opening_4]
closing_4 = }
opening_4 = !SPACE
state_4 = !ALPHA
	finish

[state_4]
state_4 = !ALPHANUM
	finish
state_body_4 = _
	finish
comma_4 = ,
pre_comma_4 = !SPACE
closing_4 = }

[state_body_4]
state_4 = !ALPHANUM
	finish
state_body_4 = _
	finish

[pre_comma_4]
pre_comma_4 = !SPACE
comma_4 = ,
closing_4 = }

[comma_4]
comma_4 = !SPACE
state_4 = !ALPHA
	finish

[closing_4]
closing_4 = !SPACE
right_4 = )

[right_4.]
right_4 = !SPACE
