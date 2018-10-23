import java.io.*;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.*;


public class SLAVE {

    public static void mkDirLauncher() throws IOException, InterruptedException {
        System.out.println("Launching mkdir command on machine: ");
        ProcessBuilder pb = new ProcessBuilder("mkdir", "-p", "/tmp/tnazon/maps");
        pb.redirectErrorStream(true);
        Process process = pb.start();
        process.waitFor();
        System.out.println("/maps dir created");
    }


    public static List<String> filesLister(String path) {
        List<String> filesList = new ArrayList<>();
        File folder = new File("your/path");
        File[] listOfFiles = folder.listFiles();

        for (int i = 0; i < listOfFiles.length; i++) {
            if (listOfFiles[i].isFile()) {
                filesList.add(listOfFiles[i].getName());
            }
        }
        return filesList;
    }


    public static void maps(String fileName, String fileNumber) throws IOException {
        List<String> lines = readLines_new(fileName);
        Set<String> listOfUniqueWords = readAndCountWords(lines, fileNumber);
        listOfUniqueWords.forEach(t -> System.out.println(t));
    }


    public static List<String> readLines_new(String fileName) {
        List<String> lines = null;
        long timespan[] = new long[2];
        try {
            // Read all files in one line - not best option for very large files //
            lines = Files.readAllLines(Paths.get(fileName), Charset.forName("UTF-8"));
        } catch (IOException e) {
            System.out.println("Erreur lors de la lecture de " + fileName);
            System.exit(1);
        }
        return lines;
    }


    public static Set<String> readAndCountWords(List<String> lines, String fileNumber) throws IOException {
        // Count method - for each word in the String split by space,
        // if the word trimmed is not empty, or a linebreak, then check if it is in the occurences HashMap
        HashMap<String, Integer> occurences = new HashMap<String, Integer>();
        Set<String> listOfUniqueWords = new HashSet<String>();
        Integer nb;
        File fout = new File("/tmp/tnazon/maps/UM" + fileNumber + ".txt");
        FileOutputStream fos = new FileOutputStream(fout);

        BufferedWriter bw = new BufferedWriter(new OutputStreamWriter(fos));

        for (String line : lines) {
            for (String word : line.split(" ")) {
                if (word.trim() != "" && word.trim() != "\t") {
                    listOfUniqueWords.add(word);
                    bw.write(word + " " + "1");
                    bw.newLine();
                }
            }
        }
        bw.close();
        return listOfUniqueWords;
    }


    public static void main(String[] args) throws InterruptedException, IOException {
        String fileNumber = args[1].substring(args[1].indexOf("/S") + 2, args[1].indexOf(".txt"));
        System.out.println(fileNumber);
        SLAVE.mkDirLauncher();
        if (args[0].equals("0")) {
            SLAVE.maps(args[1], fileNumber);
        }
    }
}
