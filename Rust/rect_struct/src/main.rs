#[derive(Debug)]
struct Rectangle {
    width: u32,
    height: u32
}

impl Rectangle {
    fn area(&self) -> u32 {
        self.width * self.height
    }

    fn square(width: u32) -> Rectangle {
        Rectangle { width, height: width }
    }
}

fn main() {
    let rect1 = Rectangle{
        width: 10,
        height: 20
    };

    println!("Rectangle: {:?} | Area: {}", rect1, rect1.area());

    let square1 = Rectangle::square(20);
    println!("Square: {:?} | Area: {}", square1, square1.area());
}