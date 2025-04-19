#!/bin/bash


source "./modules/common.sh"

akv_login() {
    echo -e "Inside func: akv_login"
}

akv_list() {
    echo -e "Inside func: akv_list"
}

akv_set() {
    echo -e "Inside func: akv_set"
}

dispatch $@
