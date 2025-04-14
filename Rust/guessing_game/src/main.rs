use std::{cmp::Ordering, io};

use colored::Colorize;
use rand::Rng;

fn main() {
    println!("Guessing game");

    let answer: u8 = rand::rng().random_range(1..101);
    println!("Actual answer is: {}", answer);

    loop {
        println!("Your guess:");
        let mut guess: String = String::new();
        io::stdin().read_line(&mut guess).expect("Stdin error");
        let guess: u8 = match guess.trim().parse() {
            Ok(num) => num,
            Err(_) => {
                println!("Invalid input");
                continue;
            }
        };
    
        match guess.cmp(&answer) {
            Ordering::Less => println!("{}", "Too Small".red()),
            Ordering::Greater => println!("{}", "Too Big".red()),
            Ordering::Equal => {
                println!("{}", "Correct Answer".green());
                break;
            },
        };
    }

    println!("\nPress enter to exit...");
    let _ = io::stdin().read_line(&mut String::new());
}
