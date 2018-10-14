import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Paths;
import java.util.*;

public class wordCount {


    public static HashMap<String, Integer> wordCount(String fileName) throws IOException {
        HashMap<String, Integer> countDict = new HashMap<String, Integer>();
        String line;
        String fileContent = fileReader(fileName);
        fileContent = fileContent.replace("\n", " ");

        String[] content = fileContent.split(" ");
        for (int i = 0; i < content.length; i++) {
            String word = content[i].trim();
            if (word != null && word != "") {
                if (countDict.get(word) != null) {
                    countDict.put(word, countDict.get(word) + 1);
                } else {
                    countDict.put(word, 1);
                }
            }
        }
        return countDict;
    }


    public static String fileReader(String fileName) throws IOException {
        String fileString;
        Scanner scanner = new Scanner(Paths.get(fileName), StandardCharsets.UTF_8.name());
        String content = scanner.useDelimiter("\\A").next();
        scanner.close();
        return content;
    }

    // this function sorts hashmap by value

    public static HashMap<String, Integer> hashByValueAndKey(HashMap<String, Integer> hm) {
        // creating list from hashmap elements
        List<Map.Entry<String, Integer>> li = new LinkedList<Map.Entry<String, Integer>> (hm.entrySet());
        // here we are sorting the list
        Collections.sort(li, new Comparator<Map.Entry<String, Integer>>() {
            public int compare(Map.Entry<String, Integer> o1, Map.Entry<String, Integer> o2) {
                int valueComparator = o1.getValue().compareTo(o2.getValue());
                int keyComparator = o1.getKey().compareTo(o2.getKey());
                if (valueComparator != 0) {
                    return -valueComparator;
                }
                return keyComparator;
            }
        });

        // add data from sorted list to hashmap
        HashMap<String, Integer> ha = new LinkedHashMap<String, Integer>();
        for(Map.Entry<String, Integer> aa : li) {
            ha.put(aa.getKey(), aa.getValue());
        }
        return ha;
    }

    public static void main(String[] args) throws IOException {
        String testText = "/home/theo/Documents/MASTER/Theo_Nazon/INF727_TP/src/input.txt";
        String longText = "/home/theo/Documents/MASTER/Theo_Nazon/INF727_TP/sante_publique.txt";
        String heavyTest = "/home/theo/Documents/MASTER/Theo_Nazon/INF727_TP/CC-MAIN-20170322212949-00140-ip-10-233-31-227.ec2.internal.warc.wet";
        long startTime = System.currentTimeMillis();
        System.out.println(hashByValueAndKey(wordCount.wordCount(testText)));
        long endTime = System.currentTimeMillis();
        long totalTime = endTime - startTime;
        System.out.println("Total execution time on the Short Text in milliseconds: " + totalTime);

        System.out.println("-------------------------");
//
        long startTime_2 = System.currentTimeMillis();
        System.out.println(hashByValueAndKey(wordCount.wordCount(longText)));
        long endTime_2 = System.currentTimeMillis();
        long totalTime_2 = endTime_2 - startTime_2;
        System.out.println("Total execution time on the Long Text in milliseconds: " + totalTime_2);

    //        System.out.println("-------------------------");
    //        long startTime_3 = System.currentTimeMillis();
    //        System.out.println(hashByValueAndKey(wordCount.wordCount(heavyTest)));
    //        long endTime_3 = System.currentTimeMillis();
    //        long totalTime_3 = endTime_3 - startTime_3;
    //        System.out.println("Total execution time on the Long Text in milliseconds: " + totalTime_3);
    }
}
