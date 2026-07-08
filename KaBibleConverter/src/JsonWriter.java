import java.io.*;
import java.nio.charset.StandardCharsets;

public class JsonWriter {

    public static void writeBook(Book book, File file) throws IOException {

        try (BufferedWriter out = new BufferedWriter(
                new OutputStreamWriter(
                        new FileOutputStream(file),
                        StandardCharsets.UTF_8))) {

            out.write("{\n");

            out.write("  \"id\": " + book.id + ",\n");

            out.write("  \"name\": \"" + escape(book.name) + "\",\n");

            out.write("  \"shortName\": \"" + escape(book.shortName) + "\",\n");

            // ---------------------------
            // Pericopes
            // ---------------------------

            out.write("  \"pericopes\": [\n");

            for (int i = 0; i < book.pericopes.size(); i++) {

                Pericope p = book.pericopes.get(i);

                out.write("    {\n");
                out.write("      \"chapter\": " + p.chapter + ",\n");
                out.write("      \"verse\": " + p.verse + ",\n");
                out.write("      \"title\": \"" + escape(p.title) + "\"\n");
                out.write("    }");

                if (i < book.pericopes.size() - 1)
                    out.write(",");

                out.write("\n");
            }

            out.write("  ],\n");

            // ---------------------------
            // Chapters
            // ---------------------------

            out.write("  \"chapters\": [\n");

            for (int c = 0; c < book.chapters.size(); c++) {

                out.write("    [\n");

                var verses = book.chapters.get(c);

                for (int v = 0; v < verses.size(); v++) {

                    Verse verse = verses.get(v);

                    out.write("      {\n");
                    out.write("        \"verse\": " + verse.verse + ",\n");
                    out.write("        \"text\": \"" + escape(verse.text) + "\"\n");
                    out.write("      }");

                    if (v < verses.size() - 1)
                        out.write(",");

                    out.write("\n");

                }

                out.write("    ]");

                if (c < book.chapters.size() - 1)
                    out.write(",");

                out.write("\n");

            }

            out.write("  ]\n");

            out.write("}\n");

        }

    }

    public static void writeBookList(
            java.util.List<String> books,
            File file) throws IOException {

        try (BufferedWriter out = new BufferedWriter(
                new OutputStreamWriter(
                        new FileOutputStream(file),
                        StandardCharsets.UTF_8))) {

            out.write("[\n");

            for (int i = 0; i < books.size(); i++) {

                out.write("  \"" + books.get(i) + "\"");

                if (i < books.size() - 1)
                    out.write(",");

                out.write("\n");

            }

            out.write("]\n");

        }

    }

    // -------------------------
    // Escape JSON text
    // -------------------------

    private static String escape(String text) {

        if (text == null)
            return "";

        StringBuilder sb = new StringBuilder();

        for (char c : text.toCharArray()) {

            switch (c) {

                case '\\':
                    sb.append("\\\\");
                    break;

                case '"':
                    sb.append("\\\"");
                    break;

                case '\n':
                    sb.append("\\n");
                    break;

                case '\r':
                    sb.append("\\r");
                    break;

                case '\t':
                    sb.append("\\t");
                    break;

                default:

                    if (c < 32) {

                        sb.append(String.format("\\u%04x", (int) c));

                    } else {

                        sb.append(c);

                    }

            }

        }

        return sb.toString();

    }

}
