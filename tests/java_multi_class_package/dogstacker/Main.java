/*
William Bailey - 
Prompt for ChatGPT-4-turbo

Please produce Java source code for a program with three classes:
- Main
- Stack
- Dog
The Dog class contains a name, date of birth, and a list of strings called tricks. The Stack is a traditional LIFO stack, and main is a demo program which pushes 5 Dog objects onto the stack, and then popped off one at a time, and printed to standard output.

Please give each of the Dog objects names which are both grand, and mocking.

*/
package dogstacker;

import java.util.Stack;

public class Main {
    public static void main(String[] args) {
        DogStack stack = new DogStack();

        Dog dog1 = new Dog("Lord Fluffington", "2018-05-21");
        dog1.learnTrick("Sit");
        dog1.learnTrick("Roll Over");
        
        Dog dog2 = new Dog("Baron von Drool", "2019-07-15");
        dog2.learnTrick("Fetch");

        Dog dog3 = new Dog("Duke Wigglebottom", "2020-01-30");
        dog3.learnTrick("Play Dead");
        dog3.learnTrick("Shake Paw");
        
        Dog dog4 = new Dog("Sir Barksalot", "2017-09-12");
        dog4.learnTrick("Jump");
        
        Dog dog5 = new Dog("Emperor Slobberface", "2021-04-05");
        dog5.learnTrick("Spin");
        
        stack.push(dog1);
        stack.push(dog2);
        stack.push(dog3);
        stack.push(dog4);
        stack.push(dog5);

        while (!stack.isEmpty()) {
            System.out.println(stack.pop());
        }
    }
}