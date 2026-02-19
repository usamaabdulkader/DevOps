echo "Enter first number: "
read f1
echo "Enter second number: "
read s1

sum=$(( $f1 + $s1 ))
prod=$(( $f1 * $s1 ))
sub=$(( $f1 - $s1 ))
div=$(( $f1 / $s1 ))
echo "$f1 + "$s1" = "$sum" $f1 - "$s1" = "$sub" $f1 x "$s1" = "$prod" $f1 / "$s1" = "$div" "


