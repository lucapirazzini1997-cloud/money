#include <stdint.h>
// Headless mGBA harness (compilare con le stesse -D della libreria: vedi prepara_emulatori.sh). Commands on stdin:
//  run N | key MASK N (hold keys for N frames) | shot FILE | ram ADDR LEN | w8/w16/w32 ADDR VAL | save FILE | load FILE | quit
#include <mgba/core/core.h>
#include <mgba/core/config.h>
#include <mgba-util/vfs.h>
#include <mgba/gba/core.h>
#include <mgba/core/serialize.h>
#include <mgba/core/log.h>
#include <stdio.h>
#include <stdarg.h>
#include <stdlib.h>
#include <string.h>
// log di mGBA spento: andrebbe su stderr, lo stesso canale delle risposte
static void nolog(struct mLogger*l,int c,enum mLogLevel lv,const char*f,va_list a){(void)l;(void)c;(void)lv;(void)f;(void)a;}
static struct mLogger quiet={.log=nolog};
int main(int argc,char**argv){
  mLogSetDefaultLogger(&quiet);
  struct mCore*core=mCoreFind(argv[1]); if(!core){fprintf(stderr,"nocore\n");return 1;}
  core->init(core); mCoreInitConfig(core,NULL);
  unsigned w,h; core->baseVideoSize(core,&w,&h);
  uint32_t*buf=calloc(w*h,4); core->setVideoBuffer(core,buf,w);
  mCoreLoadFile(core,argv[1]);
  // orologio (RTC) finto e ripetibile: 1/1/2026 12:00 piu' il tempo emulato; H_WALLCLOCK=1 per l'ora vera
  if(!getenv("H_WALLCLOCK")){ core->rtc.override=RTC_FAKE_EPOCH; core->rtc.value=1767268800000LL; }
  if(argc>2){ struct VFile*sv=VFileOpen(argv[2],O_CREAT|O_RDWR); if(sv) core->loadSave(core,sv);}
  core->reset(core);
  char line[512];
  while(fgets(line,sizeof line,stdin)){
    char c[32],a[400]; unsigned x,y;
    if(sscanf(line,"%31s",c)<1) continue;
    if(!strcmp(c,"run")){sscanf(line,"%*s %u",&x); for(unsigned i=0;i<x;i++) core->runFrame(core);}
    else if(!strcmp(c,"key")){sscanf(line,"%*s %x %u",&x,&y); core->setKeys(core,x); for(unsigned i=0;i<y;i++) core->runFrame(core); core->setKeys(core,0);}
    else if(!strcmp(c,"shot")){sscanf(line,"%*s %399s",a); FILE*f=fopen(a,"wb"); fprintf(f,"P6\n%u %u\n255\n",w,h);
      for(unsigned i=0;i<w*h;i++){unsigned p=buf[i]; fputc(p&0xff,f);fputc((p>>8)&0xff,f);fputc((p>>16)&0xff,f);} fclose(f);}
    else if(!strcmp(c,"ram")){sscanf(line,"%*s %x %u",&x,&y); for(unsigned i=0;i<y;i++) fprintf(stderr,"%02x",core->busRead8(core,x+i)); fprintf(stderr,"\n");}
    else if(!strcmp(c,"w8")){sscanf(line,"%*s %x %x",&x,&y); core->busWrite8(core,x,y);}
    else if(!strcmp(c,"w16")){sscanf(line,"%*s %x %x",&x,&y); core->busWrite16(core,x,y);}
    else if(!strcmp(c,"w32")){sscanf(line,"%*s %x %x",&x,&y); core->busWrite32(core,x,y);}
    else if(!strcmp(c,"r32")){sscanf(line,"%*s %x",&x); fprintf(stderr,"%08x\n",core->busRead32(core,x));}
    else if(!strcmp(c,"r16")){sscanf(line,"%*s %x",&x); fprintf(stderr,"%04x\n",core->busRead16(core,x));}
    else if(!strcmp(c,"r8")){sscanf(line,"%*s %x",&x); fprintf(stderr,"%02x\n",core->busRead8(core,x));}
    else if(!strcmp(c,"savestate")){sscanf(line,"%*s %399s",a); struct VFile*v=VFileOpen(a,O_CREAT|O_TRUNC|O_RDWR); mCoreSaveStateNamed(core,v,SAVESTATE_ALL); v->close(v);}
    else if(!strcmp(c,"loadstate")){sscanf(line,"%*s %399s",a); struct VFile*v=VFileOpen(a,O_RDONLY); mCoreLoadStateNamed(core,v,SAVESTATE_ALL); v->close(v);}
    else if(!strcmp(c,"ping")){fprintf(stderr,"ok\n");}
    else if(!strcmp(c,"quit")) break;
    fflush(stdout);
  }
  return 0;
}
