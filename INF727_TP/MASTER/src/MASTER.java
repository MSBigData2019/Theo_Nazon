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

    public static void mkDirLauncher(List<String> machinesList) throws IOException, InterruptedException {
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


    public static void slaveLauncher(List<String> machinesList) throws IOException, InterruptedException {

        List<String> activeMachineList = new ArrayList<String>();
        HashMap<String, Process> processMachineList = new HashMap<String, Process>();

        for (String machineName : machinesList) {
            System.out.println("ON EST LA OKLM" + machineName);
            ProcessBuilder pb = new ProcessBuilder("ssh", String.format("tnazon@%s", machineName), "java", "-jar", "/tmp/tnazon/SLAVE.jar", "0", "/tmp/tnazon/splits/S0.txt");
//            ProcessBuilder pb = new ProcessBuilder("ssh", String.format("tnazon@%s", machineName), "hostname");
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
                System.out.println(String.format("Generated output after launching slave on " + machineName + " is " +output(process.getInputStream())));
                activeMachineList.add(machineName);
            }
        }

    }

    public static void filesTransferLauncher(List<String> machinesList, List<String> filesList) throws IOException, InterruptedException {
        ArrayList<Process> processList = new ArrayList<Process>();
        int index = 0;
        int numberOfMachines = machinesList.size();
        for (String file : filesList) {
            int indexOfTargetMachine = index % numberOfMachines;
            String targetMachine = machinesList.get(indexOfTargetMachine);
            System.out.println("Launching scp command on machine: " + targetMachine);
            ProcessBuilder pb = new ProcessBuilder("scp", "/tmp/tnazon/splits/" + file, String.format("tnazon@%s:/tmp/tnazon/splits", targetMachine));
            pb.redirectErrorStream(true);
            Process process = pb.start();
            processList.add(process);
            index += 1;
        }

        for (Process process : processList) {
            int errCode = process.waitFor();
            if (errCode != 0) {
                System.out.println("Command execution generated an error of type: " + output(process.getErrorStream()));
            }
            System.out.println(output(process.getInputStream()));
        }
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

        MASTER.mkDirLauncher(activeMachineList);
        MASTER.filesTransferLauncher(activeMachineList, filesList);
        MASTER.slaveLauncher(activeMachineList);
    }

}
