#include "net/ConfigFileReader.h"
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <map>

#define MAX_PROC_NUM 10

char ProcName[48][MAX_PROC_NUM] = {0};
int nSec,ProcNum;
char Param[MAX_PROC_NUM] = {0};

typedef std::map<std::string, int> ProcMapDef;

ProcMapDef ProcMap;

void vHandleChildDeath( int n );

void deamon_init()
{
    int pid;

		signal(SIGTTOU, SIG_IGN);
		signal(SIGTTIN, SIG_IGN);
		signal(SIGTSTP, SIG_IGN);
	
		if ((pid = fork()) < 0)
		{
			printf("Failed to fork first child!\n");
			exit(1);
		}
		else if (pid > 0)
		{
			exit(0);		/*terminate parent, continue in child*/
		}
	
		/*成为本会话组的首进程*/
		setsid();
		signal(SIGHUP, SIG_IGN);
	
		/*保证本进程不是本会话组的首进程*/
		if ((pid = fork()) < 0)
		{
			printf("Failed to fork second child!\n");
			exit(1);
		}
		else if (pid > 0)
		{
			exit(0);
		}
	
		/*clear the inherited umask*/
		umask(0);	
}

void initConfig()
{
		for(int i = 0; i <= MAX_PROC_NUM;i++) {
				memset(ProcName[i],0x00,sizeof(ProcName[i]));
		}
		
		ProcMap.clear();
		CConfigFileReader config("watch_svr.conf");
		nSec = atoi(config.GetConfigName("sleep_seconds"));
		ProcNum = atoi(config.GetConfigName("proc_num"));
		if (ProcNum > 0)
		{
			for (int i = 1; i <= ProcNum; i++)
			{
				char szTemp[256] = {0};
				sprintf(szTemp, "watch_proc_%d_name", i);
				strcpy(ProcName[i], config.GetConfigName(szTemp));
				ProcMap.insert(ProcMapDef::value_type(ProcName[i], 0));
			}
		}
}

int getProcessNum(const char *pProcName)
{
    int iNum = 0;
    FILE *pPipe;
    char sShellCmd[200];
    char sBuf[200];
    memset(sShellCmd, 0, sizeof(sShellCmd));
    //sprintf(sShellCmd,"ps -ef | grep -v grep | grep -v \"sh -c\" | grep -c '%s'",pProcName);
    sprintf(sShellCmd,"ps -ef|grep '%s'|grep -v grep|wc -l",pProcName);
    if ((pPipe = popen(sShellCmd, "r")) == NULL)
    {
        return -1;
    }
    memset(sBuf, 0, sizeof(sBuf));
    fgets(sBuf, 99, pPipe);
    pclose(pPipe);
    iNum = atoi(sBuf);
    return iNum;
}

void CheckProc(const char* sProgName, const char * szParam, const int nProcNum)
{
		int		iRetCode;
		char	sShellCmd[256];
		//signal(SIGCHLD, SIG_DFL); 
		signal(SIGCHLD, SIG_IGN);
		iRetCode = getProcessNum(sProgName);
		if (iRetCode < 0) {
				printf("getProcessNum error.\n");
				return;
		}
		printf("proce %d\n",iRetCode);
		sighold( SIGCHLD );
		while (iRetCode < nProcNum)
		{
				printf("Process '%s' is invalid, start it...\n", sProgName);
				memset(sShellCmd, 0, sizeof(sShellCmd));
				sprintf(sShellCmd, "nohup %s %s ", sProgName, szParam);
				int nChildPid = 0;
				if ((nChildPid = fork()) < 0)
				{
						printf("fork child process failed\n");
						continue;
				}
				if (nChildPid == 0)//子进程
				{
						execl("/bin/sh", "sh", "-c", sShellCmd, (char *)0);
						exit(0);
				} else {
						iRetCode ++;
						ProcMap[sProgName] = nChildPid;
						printf("Process '%s' is invalid, start it ok\n", sProgName);
				}
		}
}

void vHandleChildDeath( int n )
{
    char        sFuncName[] = "vHandleChildDeath";
    int         llPid;

    while( waitpid( -1, &llPid, WNOHANG ) >0 );
    printf("%s--%d, pid '%d' \n",sFuncName,n, llPid);	
    for (int i = 1; i <= ProcNum; i++)
		{
			printf("[%s][%s][%d]\n", ProcName[i],Param,1);
			sighold( SIGCHLD );
			CheckProc(ProcName[i],Param,1);
			sigset( SIGCHLD, vHandleChildDeath );
			sigrelse( SIGCHLD );
		}
		printf("%s  end \n",sFuncName);
}

void vHandleExit( int n )
{
    char    sFuncName[] = "vHandleExit";
		printf("[%s]\n",sFuncName);
		for (int i = 1; i <= ProcNum; i++)
		{
			printf("[%s][%s][%d]\n", ProcName[i],Param,1);
			int pid = ProcMap[ProcName[i]];
			if(pid > 0){
					int ret = kill(pid,SIGTERM);
					if(ret == -1) {
							printf("stop %d error",pid);
					} else {
							printf("stop %d ok",pid);
					}
			}
		}
    exit( 1 );
}

void handleCustomSig(int sig) 
{
		char    sFuncName[] = "handleCustomSig";
		printf("[%s]  begin\n",sFuncName);
		initConfig();
		printf("[%s]  end\n",sFuncName);
}

int main(int argc, char *argv[])
{
		signal(SIGCHLD, SIG_IGN);
		deamon_init();

		sighold( SIGCHLD );
	    sigset( SIGCHLD, vHandleChildDeath );
	  sighold( SIGTERM );
	    sigset( SIGTERM, vHandleExit );
	    
		initConfig();
		sigset( SIGUSR1, handleCustomSig );
		nSec = 10;
		printf("sec[%d][%d]\n", nSec,ProcNum);
		while(TRUE)
		{
				printf("start watch...\n");
				for (int i = 1; i <= ProcNum; i ++)
				{
						printf("[%s][%s][%d]\n", ProcName[i],Param,1);
						sighold( SIGCHLD );
						CheckProc(ProcName[i],Param,1);
						sigset( SIGCHLD, vHandleChildDeath );
						sigrelse( SIGCHLD );
				}
				printf("end watch\n");
				sleep(nSec);
		}
}
