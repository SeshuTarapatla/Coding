use std::io::{self, Write};


fn get_input(prompt: &str) -> String {
    print!("{}", prompt);
    io::stdout().flush().unwrap();

    let mut input = String::new();

    io::stdin().read_line(&mut input).expect("Failed to read line");
    input.trim().to_string();
    return input;
}


fn main(){
    let path = get_input("Enter the folder: ");
    print!("You entered: {}", path);
}