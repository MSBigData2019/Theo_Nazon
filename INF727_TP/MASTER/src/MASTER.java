import java.io.*;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;

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
            System.out.println("Launching mkdir /splits/ command on machine: " + machine);
            ProcessBuilder pb = new ProcessBuilder("ssh", String.format("tnazon@%s", machine), "mkdir", "-p", "/tmp/tnazon/splits");
            pb.redirectErrorStream(true);
            Process process = pb.start();
            processList.add(process);
        }

        for (Process process : processList) {
            int errCode = process.waitFor();
            if (errCode != 0) {
                System.out.println("Unable to create dir /splits on machine : " + output(process.getErrorStream()));
            }
            System.out.println("Execution to create new directory succeeded ");
        }
    }


    public static HashMap<String, List<String>> launchSlave(List<String> machinesList, HashMap<String, List<Integer>> splitsPerMachine) throws IOException, InterruptedException {

        List<String> activeMachineList = new ArrayList<String>();
        HashMap<String, Process> processMachineList = new HashMap<String, Process>();
        HashMap<String, List<String>> UMPerMachine = new HashMap<String, List<String>>();

        for (String machineName : machinesList) {
            List<Integer> splitsForCurrentMachine = new ArrayList<Integer>();
            splitsForCurrentMachine = splitsPerMachine.get(machineName);
            for (Integer splitNumber : splitsForCurrentMachine) {
                System.out.println("ON VA LANCER LE JAR");
                ProcessBuilder pb = new ProcessBuilder("ssh", String.format("tnazon@%s", machineName), "java", "-jar", "/tmp/tnazon/SLAVE.jar", "0", String.format("/tmp/tnazon/splits/S%s.txt", splitNumber));
                // Sub-function //
                // Generate a HashMap containing the index of the splits copied to the machine, for each machine //
                List<String> list = new ArrayList<String>();
                list.add(machineName);
                String UMName = String.format("UM%s", splitNumber);
                if (UMPerMachine.containsKey(UMName)) {
                    UMPerMachine.get(UMName).add(machineName);
                } else {
                    UMPerMachine.put(UMName, list);
                }
                // End of sub-function //

                pb.redirectErrorStream(true);
                Process process = pb.start();
                processMachineList.put(machineName, process);
            }
        }

        for (Map.Entry<String, Process> entry : processMachineList.entrySet()) {
            String machineName = entry.getKey();
            Process process = entry.getValue();

            int errCode = process.waitFor();
            if (errCode != 0) {
                System.out.println("Error on launching slave jar: " + output(process.getErrorStream()) + System.getProperty("line.separator"));
            } else {
                System.out.println(String.format("Success on launching slave jar" + machineName + " is " +output(process.getInputStream())));
                activeMachineList.add(machineName);
            }
        }
        return UMPerMachine;
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
                System.out.println("Command execution generated an error of type: " + output(process.getErrorStream()));
            }
            System.out.println(output(process.getInputStream()));
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
                System.out.println("Command execution generated an error of type: " + output(process.getErrorStream()) + System.getProperty("line.separator"));
            } else {
                System.out.println("Generated output after calling hostname on is: " + output(process.getInputStream()));
                if (activeMachineList.size() < numberNodes) {
                    activeMachineList.add(machineName);
                }
            }
        }
        return activeMachineList;
    }



    public static void main(String[] args) throws InterruptedException,
            IOException {
        List<String> machinesList = MASTER.sourceReader("/tmp/tnazon/machinesnames.txt");
        List<String> filesList = new ArrayList<String>();
        filesList.add("S0.txt");
        filesList.add("S1.txt");
        filesList.add("S2.txt");

        List<String> activeMachineList = MASTER.machineTester(machinesList, 3);

        MASTER.createSplitsFolder(activeMachineList);
        HashMap<String, List<Integer>> splitsPerMachine = new HashMap<String, List<Integer>>();
        HashMap<String, List<String>> UMPerMachine = new HashMap<String, List<String>>();


        splitsPerMachine = MASTER.sendSplitsToMachines(activeMachineList, filesList);
        System.out.println(splitsPerMachine);
        UMPerMachine = MASTER.launchSlave(activeMachineList, splitsPerMachine);
        System.out.println(UMPerMachine);

    }
}
