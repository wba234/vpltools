package dogstacker;

import java.util.Stack;

class DogStack {
    private Stack<Dog> stack;

    public DogStack() {
        this.stack = new Stack<>();
    }

    public void push(Dog dog) {
        stack.push(dog);
    }

    public Dog pop() {
        return stack.pop();
    }

    public boolean isEmpty() {
        return stack.isEmpty();
    }
}
