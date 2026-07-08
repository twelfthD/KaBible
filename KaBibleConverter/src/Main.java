import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.*;

public class Main {

    public static void main(String[] args) throws Exception {

        File input;

        if (args.length > 0) {

            input = new File(args[0]);

        } else {

            input = new File("input/bible.yet");

        }

        File output = new File("output");

        if (!output.exists())
            output.mkdirs();

        Map<Integer, Book> books = new LinkedHashMap<>();

        List<String> bookFiles = new ArrayList<>();

        BufferedReader br = Files.newBufferedReader(
                input.toPath(),
                StandardCharsets.UTF_8);

        String line;

        while ((line = br.readLine()) != null) {

            if (line.isBlank())
                continue;

            String[] p = line.split("\t");

            switch (p[0]) {

                //-----------------------------------
                // Book
                //-----------------------------------

                case "book_name":

                    Book b = new Book();

                    b.id = Integer.parseInt(p[1]);

                    b.name = p[2];

                    if (p.length > 3)
                        b.shortName = p[3];

                    books.put(b.id, b);

                    break;

                //-----------------------------------
                // Pericope
                //-----------------------------------

                case "pericope":

                    Book pb = books.get(
                            Integer.parseInt(p[1]));

                    if (pb != null) {

                        pb.pericopes.add(

                                new Pericope(

                                        Integer.parseInt(p[2]),

                                        Integer.parseInt(p[3]),

                                        p[4]

                                )

                        );

                    }

                    break;

                //-----------------------------------
                // Verse
                //-----------------------------------

                case "verse":

                    int bookId =
                            Integer.parseInt(p[1]);

                    int chapter =
                            Integer.parseInt(p[2]);

                    int verse =
                            Integer.parseInt(p[3]);

                    String text = p[4];

                    Book vb = books.get(bookId);

                    if (vb == null)
                        break;

                    while (vb.chapters.size() < chapter) {

                        vb.chapters.add(
                                new ArrayList<>());

                    }

                    vb.chapters
                            .get(chapter - 1)
                            .add(new Verse(verse, text));

                    break;

            }

        }

        br.close();

        //----------------------------------------
        // Write JSON
        //----------------------------------------

        for (Book book : books.values()) {

            String fileName =

                    String.format(

                            "%02d_%s",

                            book.id,

                            sanitize(book.name)

                    );

            JsonWriter.writeBook(

                    book,

                    new File(output,

                            fileName + ".json")

            );

            bookFiles.add(fileName);

            System.out.println(

                    "Created "

                            + fileName

                            + ".json"

            );

        }

        JsonWriter.writeBookList(

                bookFiles,

                new File(output,

                        "books.json")

        );

        System.out.println();

        System.out.println(

                "Done."

        );

        System.out.println(

                books.size()

                        + " books exported."

        );

    }

    //----------------------------------------
    // Safe filename
    //----------------------------------------

    private static String sanitize(String s) {

        return s

                .trim()

                .replaceAll("[^\\p{L}\\p{N}]+", "_")

                .replaceAll("_+", "_")

                .replaceAll("^_", "")

                .replaceAll("_$", "");

    }

}
