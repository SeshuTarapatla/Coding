#!/bin/bash


# dispatch() {
#     local doc
#     local func
#     local module=$(basename "${0%.*}")
#     if [[ $1 == "-h" || $1 == "--help" || $1 == "help" ]]; then
#         func="$module"
#         doc="./docs/${module}.txt"
#     elif [[ $2 == "-h" || $2 == "--help" || $2 == "help" ]]; then
#         func="$1"
#         doc="./docs/$1.txt"
#     fi
#     if [[ -n $1 && ! $(declare -F "$1") ]]; then
#         funcs=$(declare -F | awk 'BEGIN{ORS=", "}{print $3}' | sed 's/, $//')
#         echo -e "$module: invalid function -> '$1'"
#         echo -e "functions in current scope: $funcs\n"
#         echo -e "Try: '$0 --help' for more information."
#         exit 1
#     elif [[ -n "$doc" ]]; then
#         if ! cat $doc; then
#             echo -e "\nHelp section is missing for: '$func'"
#             echo -e "Highly advised to create a help doc at: '$doc'"
#         fi
#     else
#         $@
#     fi
# }

dispatch() {
    local doc
    local func
    local module=$(basename ${0%.sh})
    local _help=("-h" "--help" "help")
    
    if [[ " ${_help[@]} " =~ " $1 " ]]; then
        func="$module"
        doc="./docs/${func}.txt"
    else
        if [[ -n $1 && ! $(declare -F "$1" 2>/dev/null) ]]; then
            funcs=$(declare -F | awk 'BEGIN{ORS=", "}{print $3}' | sed 's/, $//')
            echo -e "$module: invalid function -> '$1'"
            echo -e "functions in current scope: $funcs\n"
            echo -e "Try: '$0 --help' for more information."
            exit 1
        elif [[ " ${_help[@]} " =~ " $2 " ]]; then
            func="$1"
            doc="./docs/${func}.txt"
        fi
    fi
    if [[ -n "$doc" ]]; then
        if ! cat $doc; then
            echo -e "\nHelp section is missing for: '$func'"
            echo -e "Highly advised to create a help doc at: '$doc'"
        fi
    else
        $@
    fi
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    dispatch $@
fi
