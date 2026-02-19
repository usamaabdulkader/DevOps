
for (( i=1; i<=10; i++ )); do
    echo "$i"
done

counter=1
while [ $counter -le 10 ]
 do
    echo "$counter"
    ((counter++))
done

for i in {1..10};do
echo "$i"
done