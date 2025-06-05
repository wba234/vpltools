package dogstacker;

import java.util.List;
import java.util.ArrayList;

class Dog {
    private String name;
    private String dateOfBirth;
    private List<String> tricks;

    public Dog(String name, String dateOfBirth) {
        this.name = name;
        this.dateOfBirth = dateOfBirth;
        this.tricks = new ArrayList<>();
    }

    public void learnTrick(String trick) {
        tricks.add(trick);
    }

    @Override
    public String toString() {
        return "Dog{name='" + name + "', dateOfBirth='" + dateOfBirth + "', tricks=" + tricks + "}";
    }
}