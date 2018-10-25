import java.io.*;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.*;


public class SLAVE {

    public static void createNewDirectory(String folderName) throws IOException, InterruptedException {
        ProcessBuilder pb = new ProcessBuilder("mkdir", "-p", "/tmp/tnazon/" + folderName);
        pb.redirectErrorStream(true);
        Process process = pb.start();
        process.waitFor();
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

    public static List<String> readLines(String fileName) {
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

    // --------------------------------------------- //
    // ################ SUPPORT END ################ //
    // --------------------------------------------- //


    // ################ MAP PHASE START ############ //
    // --------------------------------------------- //

    public static void map(String fileName, String fileNumber) throws IOException {
        List<String> lines = readLines(fileName);
        Set<String> listOfUniqueWords = writeWordsToFileMap(lines, fileNumber);
        System.out.println(listOfUniqueWords);
    }

    public static Set<String> writeWordsToFileMap(List<String> lines, String fileNumber) throws IOException {
        // Count method - for each word in the String split by space,
        // if the word trimmed is not empty, or a linebreak, then check if it is in the occurences HashMap
        Set<String> listOfUniqueWords = new HashSet<String>();
        File fout = new File("/tmp/tnazon/maps/UM" + fileNumber + ".txt");
        FileOutputStream fos = new FileOutputStream(fout);

        BufferedWriter bw = new BufferedWriter(new OutputStreamWriter(fos));

        for (String line : lines) {
            for (String word : line.split(" ")) {
                if (!word.trim().equals("") && !word.trim().equals("\t")) {
                    listOfUniqueWords.add(word);
                    bw.write(word + " " + "1");
                    bw.newLine();
                }
            }
        }
        bw.close();
        return listOfUniqueWords;
    }

    // --------------------------------------------- //
    // ################ MAP PHASE END ############## //
    // --------------------------------------------- //

    // --------------------------------------------- //
    // ################ SHUFFLE START ################ //
    // --------------------------------------------- //

    public static List<String> fromFilesToList(String fileUM, String fileUMBis) {
        List<String> linesFileUM = readLines(fileUM);
        List<String> linesFileUMBis = readLines(fileUMBis);
        List<String> linesConsolidated = new ArrayList<String>();
        linesConsolidated.addAll(linesFileUM);
        linesConsolidated.addAll(linesFileUMBis);

        return linesConsolidated;
    }

    public static void shuffle(String keyToProcess, String fileNumber, String fileUM, String fileUMBis) throws IOException {
        List<String> linesConsolidated = fromFilesToList(fileUM, fileUMBis);
        writeWordsToFileShuffle(linesConsolidated, fileNumber, keyToProcess);
    }

    public static void writeWordsToFileShuffle(List<String> lines, String fileNumber, String keyToProcess) throws IOException {
        File fout = new File("/tmp/tnazon/maps/SM" + fileNumber + ".txt");
        FileOutputStream fos = new FileOutputStream(fout);

        BufferedWriter bw = new BufferedWriter(new OutputStreamWriter(fos));

        for (String line : lines) {
            for (String word : line.split(" ")) {
                if (word.equals(keyToProcess)) {
                    bw.write(word + " " + "1");
                    bw.newLine();
                }
            }
        }
        bw.close();
    }

    // --------------------------------------------- //
    // ################ SHUFFLE END ################ //
    // --------------------------------------------- //

    // --------------------------------------------- //
    // ################ REDUCE END ################ //
    // --------------------------------------------- //

    public static void reduce(String keyToProcess, String fileNumber, String fileName){
        List<String> linesFromSM = readLines(fileName);

    }

    public static void writeWordsToFileReduce(List<String> lines, String fileNumber, String keyToProcess) throws IOException {
        File fout = new File("/tmp/tnazon/reduces/RM" + fileNumber + ".txt");
        FileOutputStream fos = new FileOutputStream(fout);

        BufferedWriter bw = new BufferedWriter(new OutputStreamWriter(fos));
        Integer counterOfKey = 0;
        for (String line : lines) {
            for (String word : line.split(" ")) {
                if (word.equals(keyToProcess)) {
                    counterOfKey = counterOfKey + 1;
                }
            }
        }
        bw.write(String.format("%s %s", keyToProcess, counterOfKey));
        bw.close();
    }

    // --------------------------------------------- //
    // ################ REDUCE END ################ //
    // --------------------------------------------- //

    public static void main(String[] args) throws InterruptedException, IOException {
        Integer numberOfUMFiles = args.length;
        if (args[0].equals("0")) {
            SLAVE.createNewDirectory("maps");
            String fileNumber = args[1].substring(args[1].indexOf("/S") + 2, args[1].indexOf(".txt"));
            SLAVE.map(args[1], fileNumber);
        }
        else if (args[0].equals("1")) {
            String fileNumber = args[2].substring(args[2].indexOf("/SM") + 2, args[2].indexOf(".txt"));
            SLAVE.shuffle(args[1], fileNumber, args[3], args[4]);
        }
        else if (args[0].equals("2")) {
            String fileNumber = args[3].substring(args[3].indexOf("/SM") + 2, args[3].indexOf(".txt"));
            SLAVE.createNewDirectory("reduces");
            SLAVE.reduce(args[1], fileNumber, args[3]);

        }
    }
}
