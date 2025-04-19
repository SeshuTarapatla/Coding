#!/bin/bash


functions=()

while IFS= read -r script; do
    module=$(basename ${script%.sh})
    functions+=("$module")
    func_list=$(bash -c "source '$script'; declare -F | awk '{print \$3}'")
    while IFS= read -r func; do
        functions+=("$func")
    done <<< "$func_list"
done < <(find -mindepth 2 -type f -name "*.sh")

echo "Looping done"
echo "${functions[@]}"

for entry in ${functions[@]}; do
    if [[ -f "./docs/${entry}.txt" ]]; then
        echo "$entry : ✅"
    else
        echo "$entry : ❌"
    fi
done