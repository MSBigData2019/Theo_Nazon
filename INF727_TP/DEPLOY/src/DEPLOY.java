import java.io.*;
import java.util.*;

public class DEPLOY {

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


    public static void mkDirLauncher(List<String> machinesList) throws IOException, InterruptedException {
        ArrayList<Process> processList = new ArrayList<Process>();
        for (String machine : machinesList) {
            System.out.println("Launching mkdir command on machine: " + machine);
            ProcessBuilder pb = new ProcessBuilder("ssh", String.format("tnazon@%s", machine), "mkdir", "-p", "/tmp/tnazon");
            pb.redirectErrorStream(true);
            Process process = pb.start();
            processList.add(process);
        }

        for (Process process : processList) {
            int errCode = process.waitFor();
            if (errCode != 0) {
                System.out.println("Command execution generated an error of type: " + output(process.getErrorStream()));
            }
            System.out.println("Execution to create new directory succeeded ");
            System.out.println(output(process.getInputStream()));
        }
    }


    public static void transferLauncher(List<String> machinesList) throws IOException, InterruptedException {
//        String commandLine mm= String.format("%s, %s, %s", "ls", "-al", "tmp");
        ArrayList<Process> processList = new ArrayList<Process>();
        for (String machine : machinesList) {
            System.out.println("Launching scp command on machine: " + machine);
            ProcessBuilder pb = new ProcessBuilder("scp", "/tmp/tnazon/SLAVE.jar",String.format("tnazon@%s:/tmp/tnazon", machine));
            pb.redirectErrorStream(true);
            Process process = pb.start();
            processList.add(process);
        }

        for (Process process : processList) {
            int errCode = process.waitFor();
            if (errCode != 0) {
                System.out.println("Command execution generated an error of type: " + output(process.getErrorStream()));
            }
            System.out.println(output(process.getInputStream()));
        }
    }


    public static String output(InputStream inputStream) throws IOException {
        StringBuilder sb = new StringBuilder();
        BufferedReader br = null;
        try {
            br = new BufferedReader(new InputStreamReader(inputStream));
            String line = null;
            while ((line = br.readLine()) != null) {
                sb.append(line + System.getProperty("line.separator"));
            }
        } catch (IOException e) {
            br.close();
        }
        return sb.toString();
    }


    public static List<String> machineTester (List<String> machinesList) throws InterruptedException, IOException {
        List<String> activeMachineList = new ArrayList<String>();
        HashMap<String, Process> processMachineList = new HashMap<String, Process>();

        // Check working machines from machinesname.txt calling hostname and checking it returns machine name //
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
                activeMachineList.add(machineName);
            }
        }
        return activeMachineList;
    }

    public static void main(String[] args) throws IOException, InterruptedException {
        List<String> machinesList = DEPLOY.sourceReader("/tmp/tnazon/machinesnames.txt");
        List<String> activeMachineList = DEPLOY.machineTester(machinesList);

        DEPLOY.mkDirLauncher(activeMachineList);
        DEPLOY.transferLauncher(activeMachineList);

    }
}