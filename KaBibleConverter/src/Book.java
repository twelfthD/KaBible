import java.util.ArrayList;
import java.util.List;

public class Book {

    public int id;

    public String name;

    public String shortName = "";

    public List<List<Verse>> chapters =
            new ArrayList<>();

    public List<Pericope> pericopes =
            new ArrayList<>();

}
