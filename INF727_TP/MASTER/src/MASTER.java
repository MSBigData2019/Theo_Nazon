import java.io.*;
import java.util.*;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

public class MASTER {


    // --------------------------------------------- //
    // ################ SUPPORT BEGIN ################ //
    // --------------------------------------------- //

    // Lecture du fichier listant les differentes machines cibles du reseau //

    public static List<String> sourceReader(String fileName) throws IOException {
        List<String> listTargets = new ArrayList<String>();
        BufferedReader bf = new BufferedReader(new FileReader(fileName));
        String line = bf.readLine();
        while (line != null) {
            listTargets.add(line);
            line = bf.readLine();
        }
        return listTargets;
    }

    //  Lecture de l'output du processus //

    private static String output(InputStream inputStream) throws IOException {
        StringBuilder sb = new StringBuilder();
        BufferedReader br = null;
        try {
            br = new BufferedReader(new InputStreamReader(inputStream));
            String line = null;
            while ((line = br.readLine()) != null) {
                sb.append(line + System.getProperty("line.separator"));
            }
        } finally {
            br.close();
        }
        return sb.toString();
    }

    // --------------------------------------------- //
    // ################ SUPPORT END ################ //
    // --------------------------------------------- //

    public static void createSplitsFolder(List<String> machinesList) throws IOException, InterruptedException {
        ArrayList<Process> processList = new ArrayList<Process>();
        for (String machine : machinesList) {
//            System.out.println("Launching mkdir /splits/ command on machine: " + machine);
            ProcessBuilder pb = new ProcessBuilder("ssh", String.format("tnazon@%s", machine), "mkdir", "-p", "/tmp/tnazon/splits");
            pb.redirectErrorStream(true);
            Process process = pb.start();
            processList.add(process);
        }

        for (Process process : processList) {
            int errCode = process.waitFor();
            if (errCode != 0) {
//                System.out.println("Unable to create dir /splits on machine : " + output(process.getErrorStream()));
            }
//            System.out.println("Execution to create new directory succeeded ");
        }
    }

    public static void copyUMToSlave() {

    }

    // For a given list of {UM, Machine_1}, reverse the list
    public static Map<String, List<String>> reverseMap(Map<String, List<String>> machinePerUM) {
//        Map<String, List<String>> reversed = new HashMap<>();

        Map<String, List<String>> UMPerMachine = new HashMap<>();

        for(Map.Entry<String, List<String>> entry : machinePerUM.entrySet()){
            List<String> list = entry.getValue();
            for(String obj : list){
                if(UMPerMachine.containsKey(obj)){
                    UMPerMachine.get(obj).add(entry.getKey());
                }else{
                    UMPerMachine.put(obj, new ArrayList<String>(Arrays.asList(new String[]{entry.getKey()})));
                }
            }
        }
        return UMPerMachine;
    }

    // Goal : get a Map of the formt {Machine, UM} listing the UM to be copied to the given Machine for the
    // shuffle Phase --> output is the schemaUMPerMachine

    /// REVOIR POUR OUTPUTTER LE SCHEMA GLBOAL ET AJOUTER UN E FONCTION QUI FAIT LA DIFFERNEE 
    public static Map<String, List<String>> getListOfCopyToPerform(HashMap<String, List<String>> UMPerKey, HashMap<String, List<String>> machinePerUM) {
        Map<String, List<String>> schemaUMPerMachine = new HashMap<String, List<String>>();




        Map<String, String> keyTargetMachine = new HashMap<String, String>();


        Map<String, List<String>> UMPerMachine = reverseMap(machinePerUM);

        Iterator it = UMPerKey.entrySet().iterator();
        for(Map.Entry<String, List<String>> pair : UMPerKey.entrySet()){



            String key = pair.getKey();

            String targetMachine = new String();
            // Si la machine de l'indexe UM[0] corrreposndant a la cle n'est pas dans le schema, alors on peut choisir cette machine comme la target
            // Sinon, on prend la machine correspondant a lindex UM[1]
            //

            // key = Car
            List<String> listUMs = pair.getValue();

            // Selectionne la target machine
            for (String UM : listUMs) {
                if (schemaUMPerMachine.get(machinePerUM.get(UM)) == null) {
                    targetMachine = machinePerUM.get(UM);
                    break;
                }
            }
            if (key == "Beer") {
                targetMachine = "C45-06";
            }
            keyTargetMachine.put(key, targetMachine);
            System.out.println(String.format("For key %s, the target machine is %s", key, targetMachine));

            for (String UM : listUMs) {

                boolean UMAlreadyOnTargetMachine = UMPerMachine.get(targetMachine) == UM;


                List<String> listOfCurrentUMToBeCopied = schemaUMPerMachine.get(targetMachine);
                boolean UMAlreadyListedForCopyOnTargetMachine = Optional.ofNullable(listOfCurrentUMToBeCopied)
                        .map(l -> l.stream().anyMatch(s -> s.contains(UM)))
                        .orElse(false);
                if (!(UMAlreadyListedForCopyOnTargetMachine || UMAlreadyOnTargetMachine)) {
                    List<String> listOfNewUMToBeCopied = new ArrayList<>();
                    listOfNewUMToBeCopied.add(UM);
                    schemaUMPerMachine.put(targetMachine, listOfNewUMToBeCopied);
                }
            }
        }
        return schemaUMPerMachine;
    }





    public static HashMap<String, List<String>> launchSlave(List<String> machinesList, HashMap<String, List<Integer>> splitsPerMachine) throws IOException, InterruptedException {

        HashMap<String, Process> processList = new HashMap<String, Process>();
        HashMap<String, List<String>> machinePerUM = new HashMap<String, List<String>>();
        HashMap<String, List<String>> UMPerKey = new HashMap<String, List<String>>();


        for (String machineName : machinesList) {
            List<Integer> splitsForCurrentMachine = new ArrayList<Integer>();
            splitsForCurrentMachine = splitsPerMachine.get(machineName);
            for (Integer splitNumber : splitsForCurrentMachine) {
                ProcessBuilder pb = new ProcessBuilder("ssh", String.format("tnazon@%s", machineName), "java", "-jar", "/tmp/tnazon/SLAVE.jar", "0", String.format("/tmp/tnazon/splits/S%s.txt", splitNumber));
                // Sub-function //
                // Generate a HashMap containing the index of the splits copied to the machine, for each machine //
                // FACTORISER //
                List<String> list = new ArrayList<String>();
                list.add(machineName);
                String UMName = String.format("UM%s", splitNumber);
                if (machinePerUM.containsKey(UMName)) {
                    machinePerUM.get(UMName).add(machineName);
                } else {
                    machinePerUM.put(UMName, list);
                }
                // End of sub-function //

                pb.redirectErrorStream(true);
                Process process = pb.start();
                processList.put(UMName, process);
            }
        }

        for (Map.Entry<String, Process> entry : processList.entrySet()) {
            String UMName = entry.getKey();
            Process process = entry.getValue();
            String inputStream = output(process.getInputStream());
            int errCode = process.waitFor();

            if (errCode != 0) {
//                System.out.println("Error on launching slave jar: " + output(process.getErrorStream()) + System.getProperty("line.separator"));
            } else {
//                System.out.println(String.format("Success on launching slave jar | output is \n" + inputStream));
            }


            // FACTORISER //
            for (String word : inputStream.split( "\n")) {
                List<String> list = new ArrayList<String>();
                list.add(UMName);
                if (UMPerKey.containsKey(word)) {
                    UMPerKey.get(word).add(UMName);
                } else {
                    UMPerKey.put(word, list);
                }
            }
        }

        System.out.println("-----------------");
        System.out.println("UMs are located in the following machine");
        System.out.println(machinePerUM);

        System.out.println("-----------------");
        System.out.println("Words are located in the following UM");
        System.out.println(UMPerKey);

        System.out.println("####################");
        System.out.println("MAP PHASED COMPLETED");
        System.out.println("####################");

        return machinePerUM;
    }

    public static HashMap<String, List<Integer>> sendSplitsToMachines(List<String> machinesList, List<String> filesList) throws IOException, InterruptedException {
        ArrayList<Process> processList = new ArrayList<Process>();
        HashMap<String, List<Integer>> splitsPerMachine = new HashMap<String, List<Integer>>();
        int index = 0;
        int numberOfMachines = machinesList.size();
        System.out.println("### SENDING SPLITS ###");

        for (String file : filesList) {
            int indexOfTargetMachine = index % numberOfMachines;
            String targetMachine = machinesList.get(indexOfTargetMachine);

            // Sub-function //
            // Generate a HashMap containing the index of the splits copied to the machine, for each machine //
            List<Integer> list = new ArrayList<Integer>();
            list.add(index);
            if (splitsPerMachine.containsKey(targetMachine)) {
                splitsPerMachine.get(targetMachine).add(index);
            } else {
                splitsPerMachine.put(targetMachine, list);
            }
            // End of sub-function //

            // Sub-function //
            // Launch the process of copy for the iterated machine //
            ProcessBuilder pb = new ProcessBuilder("scp", "/tmp/tnazon/splits/" + file, String.format("tnazon@%s:/tmp/tnazon/splits", targetMachine));
            pb.redirectErrorStream(true);
            Process process = pb.start();
            processList.add(process);
            index += 1;
            // End of sub-function//
        }

        for (Process process : processList) {
            int errCode = process.waitFor();
            if (errCode != 0) {
//                System.out.println("Command execution generated an error of type: " + output(process.getErrorStream()));
            }
//            System.out.println(output(process.getInputStream()));
        }

        System.out.println("### END - SENDING SPLITS ###");
        return splitsPerMachine;
    }

    public static List<String> machineTester(List<String> machinesList, Integer numberNodes) throws IOException, InterruptedException {
        List<String> activeMachineList = new ArrayList<String>();
        HashMap<String, Process> processMachineList = new HashMap<String, Process>();

        for (String machineName : machinesList) {
            ProcessBuilder pb = new ProcessBuilder("ssh", String.format("tnazon@%s", machineName), "hostname");
            pb.redirectErrorStream(true);
            Process process = pb.start();
            processMachineList.put(machineName, process);
        }

        for (Map.Entry<String, Process> entry : processMachineList.entrySet()) {
            String machineName = entry.getKey();
            Process process = entry.getValue();

            int errCode = process.waitFor();
            if (errCode != 0) {
//                System.out.println("Command execution generated an error of type: " + output(process.getErrorStream()) + System.getProperty("line.separator"));
            } else {
//                System.out.println("Generated output after calling hostname on is: " + output(process.getInputStream()));
                if (activeMachineList.size() < numberNodes) {
                    activeMachineList.add(machineName);
                }
            }
        }
        return activeMachineList;
    }



    public static void main(String[] args) throws InterruptedException,
            IOException {
//        List<String> machinesList = MASTER.sourceReader("/tmp/tnazon/machinesnames.txt");
//        List<String> filesList = new ArrayList<String>();
//        filesList.add("S0.txt");
//        filesList.add("S1.txt");
//        filesList.add("S2.txt");
//
//        List<String> activeMachineList = MASTER.machineTester(machinesList, 3);

//        MASTER.createSplitsFolder(activeMachineList);
//        HashMap<String, List<Integer>> splitsPerMachine = new HashMap<String, List<Integer>>();
//        HashMap<String, List<String>> machinePerUM = new HashMap<String, List<String>>();


//        splitsPerMachine = MASTER.sendSplitsToMachines(activeMachineList, filesList);
//        System.out.println(splitsPerMachine);
//        machinePerUM = MASTER.launchSlave(activeMachineList, splitsPerMachine);
//        System.out.println(machinePerUM);


        HashMap<String, List<String>> UMPerKey = new HashMap<String, List<String>>();
        List<String> car = new ArrayList<>();
        car.add("UM1");
        car.add("UM2");
        List<String> beer = new ArrayList<>();
        beer.add("UM0");
        beer.add("UM2");
        List<String> deer = new ArrayList<>();
        deer.add("UM0");

        deer.add("UM2");
        List<String> river = new ArrayList<>();
        river.add("UM0");
        river.add("UM1");

        UMPerKey.put("Car", car);
        UMPerKey.put("River", river);
        UMPerKey.put("Beer", beer);
        UMPerKey.put("Deer", deer);
        System.out.println(UMPerKey);


        HashMap<String, List<String>> machinePerUM = new HashMap<>();
        List<String> machine = new ArrayList<>();
        machine.add("C45-01");
        List<String> machine2 = new ArrayList<>();
        machine.add("C45-03");
        List<String> machine3 = new ArrayList<>();
        machine.add("C45-06");
        machinePerUM.put("UM0", machine);
        machinePerUM.put("UM1", machine2);
        machinePerUM.put("UM2", machine3);

        Map<String, List<String>> bla = getListOfCopyToPerform(UMPerKey, machinePerUM);

        System.out.println(bla);

        }
}
