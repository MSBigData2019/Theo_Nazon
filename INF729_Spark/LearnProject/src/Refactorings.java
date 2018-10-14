import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;

class Refactorings {
    public static final String TXT = "txt";

    public static void main(String[] args) throws IOException {
        String[] array = getStrings(new FileReader("input." + TXT));
        Arrays.sort(array);
        for (String s : array) {
            System.out.println(s);
        }
    }

    private static String[] getStrings(FileReader fileReader) throws IOException {
        BufferedReader reader1 = new BufferedReader(fileReader);
        BufferedReader bufferedReader = reader1;
        BufferedReader bufferedReader1 = bufferedReader;
        BufferedReader reader = bufferedReader1;
        ArrayList<String> lines = new ArrayList<String>();
        String line;
        while ((line = reader.readLine()) != null) {
            lines.add(line);
        }
        reader.close();
        return lines.toArray(new String[lines.size()]);
    }
}