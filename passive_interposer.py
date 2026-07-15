from system import System_25D
import os
import util.fill_space
import subprocess
import time

class PassiveInterposer(System_25D):
    """docstring for Passive"""
    def __init__(self):
        self.chiplet_count = 0
        self.width = [None] * self.chiplet_count
        self.height = [None] * self.chiplet_count
        self.hubump = [None] * self.chiplet_count
        self.rout_hubump = [None] * self.chiplet_count
        self.power = [None] * self.chiplet_count
        self.rotation = [None] * self.chiplet_count
        self.x = [None] * self.chiplet_count
        self.y = [None] * self.chiplet_count
        self.link_type = 'nppl'
        self.length_threshold = 9

    def gen_flp(self, filename):
        # material properties
        UnderFill = "\t2.32E+06\t0.625\n"
        Copper = "\t3494400\t0.0025\n"
        Silicon = "\t1.75E+06\t0.01\n"
        resistivity_Cu = 0.0025
        resistivity_UF = 0.625
        resistivity_Si = 0.01
        specHeat_Cu = 3494400
        specHeat_UF = 2320000
        specHeat_Si = 1750000
        C4_diameter 	= 0.000250		#250um
        C4_edge 		= 0.000600 		#600um
        TSV_diameter 	= 0.000010		#10um  
        TSV_edge		= 0.000050		#50um  
        ubump_diameter 	= 0.000025		#25um
        ubump_edge 		= 0.000045		#45um
        Aratio_C4 = (C4_edge/C4_diameter)*(C4_edge/C4_diameter)-1			# ratio of white area and C4 area
        Aratio_TSV= (TSV_edge/TSV_diameter)*(TSV_edge/TSV_diameter)-1
        Aratio_ubump=(ubump_edge/ubump_diameter)*(ubump_edge/ubump_diameter)-1
        resistivity_C4=(1+Aratio_C4)*resistivity_Cu*resistivity_UF/(resistivity_UF+Aratio_C4*resistivity_Cu)
        resistivity_TSV=(1+Aratio_TSV)*resistivity_Cu*resistivity_Si/(resistivity_Si+Aratio_TSV*resistivity_Cu)
        resistivity_ubump=(1+Aratio_ubump)*resistivity_Cu*resistivity_UF/(resistivity_UF+Aratio_ubump*resistivity_Cu)
        specHeat_C4=(specHeat_Cu+Aratio_C4*specHeat_UF)/(1+Aratio_C4)
        specHeat_TSV=(specHeat_Cu+Aratio_TSV*specHeat_Si)/(1+Aratio_TSV)
        specHeat_ubump=(specHeat_Cu+Aratio_ubump*specHeat_UF)/(1+Aratio_ubump)
        mat_C4 = "\t"+str(specHeat_C4)+"\t"+str(resistivity_C4)+"\n"
        mat_TSV = "\t"+str(specHeat_TSV)+"\t"+str(resistivity_TSV)+"\n"
        mat_ubump = "\t"+str(specHeat_ubump)+"\t"+str(resistivity_ubump)+"\n"

        # with open(self.path + filename+ 'L0_Substrate.flp','w') as L0_Substrate:
        # 	L0_Substrate.write("# Floorplan for Substrate Layer with size "+str(self.intp_size/1000)+"x"+str(self.intp_size/1000)+" m\n")
        # 	L0_Substrate.write("# Line Format: <unit-name>\\t<width>\\t<height>\\t<left-x>\\t<bottom-y>\\t[<specific-heat>]\\t[<resistivity>]\n")
        # 	L0_Substrate.write("# all dimensions are in meters\n")
        # 	L0_Substrate.write("# comment lines begin with a '#' \n")
        # 	L0_Substrate.write("# comments and empty lines are ignored\n\n")
        # 	L0_Substrate.write("Substrate\t"+str(self.intp_size/1000)+"\t"+str(self.intp_size/1000)+"\t0.0\t0.0\n")
        # os.system("perl util/tofig.pl -f 20 "+self.path+filename+"L0_Substrate.flp | fig2dev -L ps | ps2pdf - "+self.path+filename+"L0_Substrate.pdf")

        # with open(self.path+filename +'L1_C4Layer.flp','w') as L1_C4Layer:
        # 	L1_C4Layer.write("# Floorplan for C4 Layer \n")
        # 	L1_C4Layer.write("# Line Format: <unit-name>\\t<width>\\t<height>\\t<left-x>\\t<bottom-y>\\t[<specific-heat>]\\t[<resistivity>]\n")
        # 	L1_C4Layer.write("# all dimensions are in meters\n")
        # 	L1_C4Layer.write("# comment lines begin with a '#' \n")
        # 	L1_C4Layer.write("# comments and empty lines are ignored\n\n")
        # 	L1_C4Layer.write("C4Layer\t"+str(self.intp_size / 1000)+"\t"+str(self.intp_size / 1000)+"\t0.0\t0.0"+mat_C4)
        # os.system("perl util/tofig.pl -f 20 "+self.path+filename+"L1_C4Layer.flp | fig2dev -L ps | ps2pdf - "+self.path+filename+"L1_C4Layer.pdf")

        with open(self.path+filename +'L0_Interposer.flp','w') as L0_Interposer:
            L0_Interposer.write("# Floorplan for Silicon Interposer Layer\n")
            # L0_Interposer.write("# Line Format: <unit-name>\\t<width>\\t<height>\\t<left-x>\\t<bottom-y>\\t[<specific-heat>]\\t[<resistivity>]\n")
            # L0_Interposer.write("# all dimensions are in meters\n")
            # L0_Interposer.write("# comment lines begin with a '#' \n")
            # L0_Interposer.write("# comments and empty lines are ignored\n\n")
            L0_Interposer.write("Interposer\t"+str(self.intp_size / 1000)+"\t"+str(self.intp_size / 1000)+"\t0.0\t0.0\n")
        # os.system("perl util/tofig.pl -f 20 "+self.path+filename+"L0_Interposer.flp | fig2dev -L ps | ps2pdf - "+self.path+filename+"L0_Interposer.pdf")

        # with open(self.path+filename + 'sim.flp','w') as SIMP:
        with open(self.path + filename + 'L1_UbumpLayer.flp', 'w') as L1_UbumpLayer:
            with open(self.path + filename + 'L2_ChipLayer.flp', 'w') as L2_ChipLayer:
                L1_UbumpLayer.write("# Floorplan for Microbump Layer \n")
                # L1_UbumpLayer.write("# Line Format: <unit-name>\\t<width>\\t<height>\\t<left-x>\\t<bottom-y>\\t[<specific-heat>]\\t[<resistivity>]\n")
                # L1_UbumpLayer.write("# all dimensions are in meters\n")
                # L1_UbumpLayer.write("# comment lines begin with a '#' \n")
                # L1_UbumpLayer.write("# comments and empty lines are ignored\n\n")
                L2_ChipLayer.write("# Floorplan for Chip Layer\n")
                # L2_ChipLayer.write("# Line Format: <unit-name>\\t<width>\\t<height>\\t<left-x>\\t<bottom-y>\\t[<specific-heat>]\\t[<resistivity>]\n")
                # L2_ChipLayer.write("# all dimensions are in meters\n")
                # L2_ChipLayer.write("# comment lines begin with a '#' \n")
                # L2_ChipLayer.write("# comments and empty lines are ignored\n\n")
                edge_0_str = "Corner_0\t" + str(self.granularity / 1000) + "\t" + str(self.granularity / 1000) + "\t0.0\t0.0\n"
                edge_1_str = "Corner_1\t" + str(self.granularity / 1000) + "\t" + str(self.granularity / 1000) + "\t"+str(self.intp_size / 1000 - self.granularity / 1000)+"\t0.0\n"
                edge_2_str = "Corner_2\t" + str(self.granularity / 1000) + "\t" + str(self.granularity / 1000) + "\t0.0\t"+str(self.intp_size / 1000 - self.granularity / 1000) + "\n"
                edge_3_str = "Corner_3\t" + str(self.granularity / 1000) + "\t" + str(self.granularity / 1000) + "\t"+str(self.intp_size / 1000 - self.granularity / 1000)+"\t"+ str(self.intp_size / 1000 - self.granularity / 1000)+"\n"
                L1_UbumpLayer.write(edge_0_str)
                L1_UbumpLayer.write(edge_1_str)
                L1_UbumpLayer.write(edge_2_str)
                L1_UbumpLayer.write(edge_3_str)
                L2_ChipLayer.write(edge_0_str)
                L2_ChipLayer.write(edge_1_str)
                L2_ChipLayer.write(edge_2_str)
                L2_ChipLayer.write(edge_3_str)

                x_offset0, y_offset0 = self.granularity / 2 / 1000, self.granularity / 2 / 1000
                index_ubump = 0
                for i in range(0, self.chiplet_count):
                    x_offset1 = self.x[i] / 1000 - self.width[i] / 1000 * 0.5 - self.hubump[i] / 1000
                    y_offset1 = self.y[i] / 1000 - self.height[i] / 1000 * 0.5 - self.hubump[i] / 1000
                    # TODO: no hubump for hotspot thermal
                    if self.hubump[i] > 0:
                        L1_UbumpLayer.write("Ubump_"+str(index_ubump)+"\t"+str(self.width[i] / 1000 + self.hubump[i] / 1000)+"\t"+str(self.hubump[i] / 1000)+"\t"+str(x_offset1)+"\t"+str(y_offset1)+mat_ubump)
                        L1_UbumpLayer.write("Ubump_"+str(index_ubump+1)+"\t"+str(self.hubump[i] / 1000)+"\t"+str(self.height[i] / 1000 + self.hubump[i] / 1000)+"\t"+str(x_offset1)+"\t"+str(y_offset1+self.hubump[i] / 1000)+mat_ubump)
                        L1_UbumpLayer.write("Ubump_"+str(index_ubump+2)+"\t"+str(self.hubump[i] / 1000)+"\t"+str(self.height[i] / 1000 + self.hubump[i] / 1000)+"\t"+str(x_offset1+self.width[i] / 1000 + self.hubump[i] / 1000)+"\t"+str(y_offset1)+mat_ubump)
                        L1_UbumpLayer.write("Ubump_"+str(index_ubump+3)+"\t"+str(self.width[i] / 1000 + self.hubump[i] / 1000)+"\t"+str(self.hubump[i] / 1000)+"\t"+str(x_offset1+self.hubump[i] / 1000)+"\t"+str(y_offset1+self.height[i] / 1000 + self.hubump[i] / 1000)+mat_ubump)
                        L2_ChipLayer.write("Ubump_"+str(index_ubump)+"\t"+str(self.width[i] / 1000 + self.hubump[i] / 1000)+"\t"+str(self.hubump[i] / 1000)+"\t"+str(x_offset1)+"\t"+str(y_offset1)+Silicon)
                        L2_ChipLayer.write("Ubump_"+str(index_ubump+1)+"\t"+str(self.hubump[i] / 1000)+"\t"+str(self.height[i] / 1000 + self.hubump[i] / 1000)+"\t"+str(x_offset1)+"\t"+str(y_offset1+self.hubump[i] / 1000)+Silicon)
                        L2_ChipLayer.write("Ubump_"+str(index_ubump+2)+"\t"+str(self.hubump[i] / 1000)+"\t"+str(self.height[i] / 1000 + self.hubump[i] / 1000)+"\t"+str(x_offset1+self.width[i] / 1000 + self.hubump[i] / 1000)+"\t"+str(y_offset1)+Silicon)
                        L2_ChipLayer.write("Ubump_"+str(index_ubump+3)+"\t"+str(self.width[i] / 1000 + self.hubump[i] / 1000)+"\t"+str(self.hubump[i] / 1000)+"\t"+str(x_offset1+self.hubump[i] / 1000)+"\t"+str(y_offset1+self.height[i] / 1000 + self.hubump[i] / 1000)+Silicon)
                        index_ubump += 4
                    # not sure about the microbump density for the center region. Assume the same as the edge area so far. Need to be updated if the microbump pitch for center power/gnd clk is found
                    L1_UbumpLayer.write("Chiplet_"+str(i)+"\t"+str(self.width[i] / 1000)+"\t"+str(self.height[i] / 1000)+"\t"+str(x_offset1 + self.hubump[i] / 1000)+"\t"+str(y_offset1+self.hubump[i] / 1000)+mat_ubump)
                    L2_ChipLayer.write("Chiplet_"+str(i)+"\t"+str(self.width[i] / 1000)+"\t"+str(self.height[i] / 1000)+"\t"+str(x_offset1 + self.hubump[i] / 1000)+"\t"+str(y_offset1+self.hubump[i] / 1000)+Silicon)
                    # SIMP.write("Unit_"+str(i)+"\t"+str(self.width[i] / 1000 + 2 * self.hubump[i] / 1000)+"\t"+str(self.height[i] / 1000 + 2 * self.hubump[i] / 1000)+"\t"+str(x_offset1)+"\t"+str(y_offset1)+"\n")
        # os.system("perl util/tofig.pl -f 20 "+self.path+filename+"L3.flp | fig2dev -L ps | ps2pdf - "+self.path+filename+"L3.pdf")
        # os.system("perl util/tofig.pl -f 20 "+self.path+filename+"L4.flp | fig2dev -L ps | ps2pdf - "+self.path+filename+"L4.pdf")
        if False:
            os.system(f"python3 util/hotspot_scripts/visualize_floorplan.py {self.path+filename+'L1_UbumpLayer.flp'} {self.path+filename+'L1_UbumpLayer.png'}")
            os.system(f"python3 util/hotspot_scripts/visualize_floorplan.py {self.path+filename+'L2_ChipLayer.flp'} {self.path+filename+'L2_ChipLayer.png'}")

        # util.fill_space.fill_space(x_offset0, self.intp_size / 1000 - x_offset0, y_offset0, self.intp_size / 1000 - y_offset0, self.path+filename+'sim', self.path+filename+'L3', self.path+filename+'L3_UbumpLayer')
        # util.fill_space.fill_space(x_offset0, self.intp_size / 1000 - x_offset0, y_offset0, self.intp_size / 1000 - y_offset0, self.path+filename+'sim', self.path+filename+'L4', self.path+filename+'L4_ChipLayer')
        # os.system("perl util/tofig.pl -f 20 "+self.path+filename+"L3_UbumpLayer.flp | fig2dev -L ps | ps2pdf - "+self.path+filename+"L3_UbumpLayer.pdf")
        # os.system("perl util/tofig.pl -f 20 "+self.path+filename+"L4_ChipLayer.flp | fig2dev -L ps | ps2pdf - "+self.path+filename+"L4_ChipLayer.pdf")

        with open(self.path+filename +'L3_TIM.flp','w') as L3_TIM:
            L3_TIM.write("# Floorplan for TIM Layer \n")
            # L3_TIM.write("# Line Format: <unit-name>\\t<width>\\t<height>\\t<left-x>\\t<bottom-y>\\t[<specific-heat>]\\t[<resistivity>]\n")
            # L3_TIM.write("# all dimensions are in meters\n")
            # L3_TIM.write("# comment lines begin with a '#' \n")
            # L3_TIM.write("# comments and empty lines are ignored\n\n")
            L3_TIM.write("TIM\t"+str(self.intp_size / 1000)+"\t"+str(self.intp_size / 1000)+"\t0.0\t0.0\n")
        # os.system("perl util/tofig.pl -f 20 "+self.path+filename+"L3_TIM.flp | fig2dev -L ps | ps2pdf - "+self.path+filename+"L3_TIM.pdf")

        path = os.path.abspath(self.path)
        with open(self.path+filename + 'layers.lcf','w') as LCF:
            LCF.write("# File Format:\n")
            LCF.write("#<Layer Number>\n")
            LCF.write("#<Lateral heat flow Y/N?>\n")
            LCF.write("#<Power Dissipation Y/N?>\n")
            LCF.write("#<Specific heat capacity in J/(m^3K)>\n")
            LCF.write("#<Resistivity in (m-K)/W>\n")
            LCF.write("#<Thickness in m>\n")
            LCF.write("#<floorplan file>\n")
            # LCF.write("\n# Layer 0: substrate\n0\nY\nN\n1.06E+06\n3.33\n0.0002\n"+os.path.join(path, filename+"L0_Substrate.flp")+"\n")
            # LCF.write("\n# Layer 1: Epoxy SiO2 underfill with C4 copper pillar\n1\nY\nN\n2.32E+06\n0.625\n0.00007\n"+os.path.join(path, filename+"L1_C4Layer.flp")+"\n")
            LCF.write("\n# Layer 0: silicon interposer\n0\nY\nN\n1.75E+06\n0.01\n0.00011\n"+os.path.join(path, filename+"L0_Interposer.flp")+"\n")
            LCF.write("\n# Layer 1: Underfill with ubump\n1\nY\nN\n2.32E+06\n0.625\n1.00E-05\n"+os.path.join(path, filename+"L1_UbumpLayer.flp")+"\n")
            LCF.write("\n# Layer 2: Chip layer\n2\nY\nY\n2.32E+06\n0.625\n0.00015\n"+os.path.join(path, filename+"L2_ChipLayer.flp")+"\n")
            LCF.write("\n# Layer 3: TIM\n3\nY\nN\n4.00E+06\n0.25\n2.00E-05\n"+os.path.join(path, filename+"L3_TIM.flp")+"\n")

        if os.path.isfile(self.path + 'new_hotspot.config') == False:
            with open('util/hotspot.config','r') as Config_in:
                with open(self.path + 'new_hotspot.config','w') as Config_out:
                    # size_spreader = 2 * self.intp_size / 1000
                    # size_heatsink = 2 * size_spreader
                    # r_convec =  0.1 * 0.06 * 0.06 / size_heatsink / size_heatsink   #0.1*0.06*0.06 are from default hotspot.config file
                    for line in Config_in:
                        Config_out.write(line)
                    # 	if line.strip().startswith('-s_sink'):
                    # 		Config_out.write(f'		-s_sink			{size_heatsink:.2f}\n')
                    # 	elif line.strip().startswith('-s_spreader'):
                    # 		Config_out.write(f'		-s_spreader			{size_spreader:.2f}\n')
                    # 	elif line.strip().startswith('-r_convec'):
                    # 		Config_out.write(f'		-r_convec			{r_convec:.2f}\n')
                    # 	else:
                            # Config_out.write(line)

    def gen_ptrace(self, filename):
        num_component = 0
        component, component_name, component_index = [], [], []
        # Read components from flp file
        with open (self.path + filename + 'L2_ChipLayer.flp','r') as FLP:
            for line in FLP:
                line_sp = line.split()
                if line_sp:
                    if line_sp[0] != '#':
                        component.append(line_sp[0])
                        comp = component[num_component].split('_')
                        component_name.append(comp[0])
                        component_index.append(int(comp[1]))
                        num_component+=1	

        with open (self.path + filename + '.ptrace','w') as Ptrace:
            # Write ptrace header
            for i in range(0,num_component):
                # if component_name[i] == 'Core':
                Ptrace.write(component[i]+'\t')
            Ptrace.write('\n')
            for i in range(0,num_component):
                if component_name[i] == 'Chiplet':
                    Ptrace.write(str(self.power[component_index[i]])+'\t')
                # elif component_name[i] == 'Ubump':
                # 	Ptrace.write('0.3\t')
                else:
                    Ptrace.write('0.0\t')
            Ptrace.write('\n')

    def run_hotspot(self, filename):
        path = os.path.abspath(self.path)
        cmd = ["./hotspot",
            "-c",os.path.join(path,"new_hotspot.config"),
            "-f",os.path.join(path,filename+"L2_ChipLayer.flp"),
            "-p",os.path.join(path,filename+".ptrace"),
            "-steady_file",os.path.join(path,filename+".steady"),
            "-grid_steady_file",os.path.join(path,filename+".grid.steady"),
            "-model_type","grid",
            "-detailed_3D","on",
            "-grid_layer_file",os.path.join(path,filename+"layers.lcf")]
        # TODO: sel hotspot bin version
        if True:
            cwd = "hotspot_with_model_extract"
            # outlist_start_label = 42
            outlist_start_label = 26 # removed dump code results 26
        else:
            cwd = "util"
            outlist_start_label = 3
        proc = subprocess.Popen(cmd, 
            stdout=subprocess.PIPE, stderr = subprocess.PIPE, cwd=cwd)
        stdout, stderr = proc.communicate()
        outlist = stdout.split()
        if proc.returncode != 0:
            with open(self.path + filename + '_hotspot.log', 'w') as Output:
                Output.write("--> Command:\n")
                Output.write(" ".join(cmd)+"\n")
                Output.write("--> stderr:\n")
                Output.write(stderr.decode())
                Output.write("--> stdout:\n")
                Output.write(stdout.decode())
            raise RuntimeError(
                f"hotspot failed with exit code {proc.returncode}. See {self.path + filename + '_hotspot.log'}"
            )

        # plot fig
        # TODO: fixed layer number
        if False:
            os.system(f"python3 util/hotspot_scripts/split_grid_steady.py {os.path.join(path,filename+'.grid.steady')} 6 64 64")
            os.system(f"python3 util/hotspot_scripts/grid_thermal_map.py {os.path.join(path,filename+'L2_ChipLayer.flp')} {os.path.join(path,filename+'_layer2.grid.steady')} {os.path.join(path,filename+'_layer2.png')}")

        # report temp
        try:
            temps = []
            for i in range(self.chiplet_count):
                # TODO: fixed layer number
                idx = outlist.index(bytes("layer_2_Chiplet_"+str(i), 'utf-8'))
                temps.append(round(float(outlist[idx+1])-273.15, 2))
            print(f"Chiplet temps: {temps}")
        except ValueError:
            print ('layer_2_Chiplet_i not found')
        return (max(list(map(float,outlist[outlist_start_label::2])))-273.15)

    def clean_hotspot(self, filename):
        # TODO: wait time sleep
        if False:
            print("*** start to wait ...")
            time.sleep(5)
        # os.system('rm ' + self.path + filename + '{*.flp,*.lcf,*.ptrace,*.steady}')
        os.system('rm ' + self.path + filename + '*.flp')
        os.system('rm ' + self.path + filename + '*.lcf')
        os.system('rm ' + self.path + filename + '*.ptrace')
        os.system('rm ' + self.path + filename + '*.steady')
        os.system('rm ' + self.path + filename + '*.png')

    def compute_ubump_overhead(self):
        # print (self.link_type)
        connection = self.connection_matrix
        for i in range(self.chiplet_count):
            assert connection[i][i] == 0, 'a link from and to the same chiplet is not allowed'
            s = 0
            for j in range(self.chiplet_count):
                s += connection[i][j] + connection[j][i]
            if self.link_type == 'ppl':
                s *= 2
            h = 1
            w_stretch = 0.045 * h
            while ((self.width[i] + self.height[i]) * 2 * w_stretch + 4 * w_stretch * w_stretch) / 0.045 / 0.045 < s:
                h += 1
                w_stretch = 0.045 * h
                if h > 1000:
                    print ('microbump is too high to be a feasible case')
                    exit()
            # print (i, s, self.width[i], self.height[i], h, w_stretch)
            # TODO: thermal eval without microbump overhead
            self.rout_hubump[i] = w_stretch
            if True:
                self.hubump[i] = 0.0
            else:
                self.hubump[i] = w_stretch
        # print (self.hubump)

    def set_link_type(self, link_type):
        self.link_type = link_type