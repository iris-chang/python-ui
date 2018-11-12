import PySimpleGUI as sg
import webbrowser
import os
import time
import csv

src_path=''

def import_osm_UI(dest_path, skip_check=False):
    """
    Temporary UI dialogue that manage import of osm file
    Note: Does NOT handle OSM to DB conversion
    :return osm_file_path
    """
    if not skip_check:
        layout = [[sg.Text('\nHave you downloaded your data from OSM?', font=("Helvetica", 12))],
                  [sg.Text('Press YES to proceed, press NO to open OSM', font=("Helvetica", 8), size=(50, 1), text_color="red")],
                  [sg.Text('')],
                  [sg.CButton('Yes'), sg.Button("No", )],
                  [sg.Text('')]]
        window9 = sg.Window('Sample GUI', grab_anywhere=False).Layout(layout)
        # diplays the form, collects the information and returns the data collected
        button9, values9 = window9.Read()

        if button9 is None:
            return None

        while button9 == "No":
            webbrowser.open_new("https://www.openstreetmap.org")
            button9, values = window9.Read()
            if button9 == "Yes":
                break
            if button9 is None:
                return None

    # flags for checking for valid input
    inputFlag = None
    osm_filepath = ""

    while inputFlag is not True:
        layout = [[sg.Text('\nOSM File Name')],
                  [sg.Text('*Please choose a valid OSM file', text_color='red', font=("Helvetica", 8))] if inputFlag is False else [],
                  [sg.Input(default_text=osm_filepath, change_submits=True, key='filepath_input', do_not_clear=True), sg.FileBrowse(file_types=(("OSM Files", "*.osm"),), initial_folder=dest_path)],
                  [sg.Text('\n', text_color='grey')],
                  [sg.Text('', font=("Helvetica", 4))],
                  [sg.CButton('Submit')]]

        window8 = sg.Window('Create Database', grab_anywhere=False).Layout(layout)
        while True:
            button8, values = window8.Read()
            osm_filepath = values['filepath_input']
            if button8 is None:
                return None
            elif button8 == 'filepath_input':
                window8.BringToFront()
            elif button8 == 'Submit':
                inputFlag = True if osm_filepath != "" and osm_filepath[-4:] == '.osm' else False
                if inputFlag is True:
                    break
                else:
                    sg.PopupError("Please choose a valid OSM file")

    return osm_filepath


def select_highway_UI():
    """
    Temporary UI dialogue for selecting highway values
    :return: list of highway values selected
    """
    highway_options = ['<select>',  # (do not remove) placeholder so the options list will never be empty
                       'motorway',
                       'trunk',
                       'tertiary',
                       'unclassified',
                       'residential',
                       'service']

    defaults = ['primary', 'secondary']

    highway_selected = defaults.copy()
    button_ex = ''

    highway_options.sort()
    highway_selected.sort()

    # Note about this section: make sure that neither of the Listboxes ever becomes empty
    while button_ex != "Yes":
        layout = [[sg.Column([[sg.Text('Highway Value Options')], [sg.Listbox(key='options', values=highway_options, size=(30, 6), select_mode='multiple', bind_return_key=True)]]),
                   sg.Column([[sg.Text('\n')],[sg.Button('>')], [sg.Button('<')]]),
                   sg.Column([[sg.Text('Highway Value Selected')], [sg.Listbox(key='selected', values=highway_selected, size=(30, 6), select_mode='multiple', bind_return_key=True)]])],
                  [sg.Text('', key='warning', text_color='red', size=(50, 1))],
                  [sg.CButton('Submit')]]
        window10 = sg.Window('Analysis Parameters - Highway Values', grab_anywhere=False).Layout(layout)
        button10, values = window10.Read()
        while True:
            #print(values['options'], values['selected'])
            if button10 is None:
                return None
            elif button10 == 'Submit':
                if len(highway_selected) > 0:
                    button_ex = "Yes"    # prevent the highway values selection UI from activating again
                break
            else:
                if button10 == '>' or button10 == 'options':
                    highway_selected.extend(values['options'])
                    if '<select>' in values['options']:
                        highway_selected.remove('<select>')
                    highway_options = [op for op in highway_options if op == '<select>' or op not in values['options']]
                elif button10 == '<' or button10 == 'selected':
                    if len(values['selected']) == len(highway_selected):
                        window10.FindElement('warning').Update('At least 1 highway value must be selected')
                    else:
                        highway_options.extend(values['selected'])
                        highway_selected = [op for op in highway_selected if op not in values['selected']]
                highway_options.sort()
                highway_selected.sort()
                window10.FindElement('selected').Update(values=highway_selected)
                window10.FindElement('options').Update(values=highway_options)

                button10, values = window10.Read()
                window10.FindElement('warning').Update('')

        # print(highway_selected)
        return highway_selected


def create_network(newNet, selected_highway, root_path, create_shapefiles):
    """
    Creates loading progress bar and window for UI
    Also handles the creation of the network by calling functions from NetworkCreation class

    :param newNet: NetworkCreation object from rubelMain (network not yet created)
    :param selected_highway: list of highway values selected
    :param root_path: filepath of output folder
    :param create_shapefiles: flag for whether to create shapefiles (True/False)
    :return:
    """
    createNetworkShapeFile = create_shapefiles
    print("Creating Network: \n ......")
    length = 1000
    layout = [[sg.Text('Creating Network from OSM...')],
              [sg.ProgressBar(length*1.5, orientation='h', size=(20, 20), key='progress')]]
    window1 = sg.Window('Creating Network').Layout(layout)
    progress_bar = window1.FindElement('progress')
    for i in range(length):
        exe_per_loop_foo(i)
        if i % (length//10) == 0:
            button, values = window1.Read(timeout=10)
            if values is None:
                return None
            progress_bar.UpdateBar(i)
    after_loop_foo()
    progress_bar.UpdateBar(length*1.5//2+i//2)
    current_bar = length*1.5//2+i//2
    n = 0
    ph_num = 100  # placeholder
    for i in range(ph_num):
        time.sleep(0.3)
        if i % (ph_num//5) == 0:
            n += 1
            button, values = window1.Read(timeout=10)
            if values is None:
                return None
            progress_bar.UpdateBar(current_bar + n*(length*1.5-current_bar)//10)
    for i in range(ph_num):
        time.sleep(0.2)
        if i % (ph_num//5) == 0:
            n += 1
            button, values = window1.Read(timeout=10)
            if values is None:
                return None
            progress_bar.UpdateBar(current_bar + n*(length*1.5-current_bar)//10)
    after_loop_foo()
    progress_bar.UpdateBar(length * 1.5)
    window1.Close()
    if createNetworkShapeFile:
        # shp_dest = create_folder(root_path, 'Output files1')
        layout = [[sg.Text('Creating output files\nfor network...')]]
        window5 = sg.Window('Loading')
        window5.Layout(layout).Read(timeout=10)
        placeholder_network_foo()
        window5.Close()
    print("network Generation completed\n........\n ")
    return True

def calculate_shortest_path(newNet, root_path):
    """
    Temporary UI dialogue boxes, allows options of 1. from CSV or 2. from 2 points
    Creates ShortestPathRD (from rubelMain) object to calculate shortest path

    :param newNet: NetworkCreation object (with network created)
    :param root_path: filepath of output folder
    :return:
    """
    frame_layout = [[sg.Radio('From CSV', 'path_cal', default=True)],
                    [sg.Radio('From 2 points', 'path_cal')]]
    layout = [[sg.Text("Network generation completed", pad=(2, 8))],
              [sg.Frame(' Compute Shortest Path ', frame_layout, font=14, title_color='dim grey', title_location='nw', pad=(8, 15))],
              [sg.CButton('Submit')]]
    window11 = sg.Window('Network Created', grab_anywhere=False).Layout(layout)
    button2, values = window11.Read()
    if button2 is None:
        return None
    elif button2 == 'Submit':
        path_input = 'CSV' if values[0] is True else '2pts'
    if path_input == '2pts':
        while True:
            frame_layout = [[sg.Text("Start point: [0 to n]", size=(23, 1), pad=(2, 8)), sg.Input(key='start_pt', size=(5,1))],
                            [sg.Text("End point: [0 to n]", size=(23, 1), pad=(2, 8)), sg.Input(key='end_pt', size=(5,1))]]
            layout = [[sg.Frame(' Enter Start and End Points ', frame_layout, font=14, title_color='dim grey', title_location='nw', pad=(8,15))],
                      [sg.CButton('Submit')]]
            window12 = sg.Window('Calculate Shortest Path - Input', grab_anywhere=False).Layout(layout)
            button2, values = window12.Read()

            if button2 is None:
                return None
            else:
                try:
                    path_pts = [values['start_pt'], values['end_pt']]
                    layout = [[sg.Text('Calculating shortest path...')]]
                    window3 = sg.Window('Loading')
                    window3.Layout(layout).Read(timeout=10)
                    time.sleep(2)  # placeholder
                    window3.Close()
                    if True:  # actual checking was stripped for this pureUI demo
                        frame_layout = [[sg.Checkbox('  Shapefiles', key='create_shp', pad=(25,2), tooltip='Create shapefiles for shortest path')],
                                        [sg.Checkbox('  CSV File', key='create_csv', pad=(25,2), tooltip='Create CSV file containing all intersection nodes and final distance')],
                                        [sg.Text('      '), sg.CButton('Next')]]
                        layout = [[sg.Text('From point %s to point %s' % (path_pts[0], path_pts[1]))],
                                  [sg.Text(" the shortest path is", pad=(0, 3)), sg.Text('123.4 km', text_color='red')],
                                  [sg.Frame(' Save Results ', frame_layout, font=14, title_color='dim grey', title_location='nw', pad=(8, 15))]]
                        window13 = sg.Window('Calculation complete', grab_anywhere=False).Layout(layout)
                        button2, values = window13.Read()

                        if button2 is None:
                            return None
                        elif button2 == 'Next':
                            createPathShapeFile = values['create_shp']
                            createCSVFile = values['create_csv']
                        else:
                            createPathShapeFile = False
                            createCSVFile = False

                        if createCSVFile or createPathShapeFile:
                            # dest_fold = create_folder(root_path, 'Output files2')
                            if createPathShapeFile:
                                layout = [[sg.Text('Creating shapefiles for shortest path...')]]
                                window4 = sg.Window('Loading')
                                window4.Layout(layout).Read(timeout=10)
                                time.sleep(2)
                                window4.Close()
                            if createCSVFile:
                                pass

                        recal_text = '\n' + ('Shapefiles ' if createPathShapeFile else '') +\
                                     ('and ' if createCSVFile and createPathShapeFile else '') + \
                                     ('CSV file ' if createCSVFile else '') + ('have ' if createPathShapeFile and createCSVFile else ('has ' if createCSVFile or createPathShapeFile else '')) +\
                                      'been created\n\n' if createPathShapeFile or createCSVFile else ''
                        recalculate = sg.PopupYesNo(recal_text + 'Calculate new path?\n')
                        if recalculate == 'No':
                            break
                        elif recalculate is None:
                            return None
                except ValueError:
                    sg.PopupError('Please enter valid\nstart and end points\n')
    elif path_input == 'CSV':
        while True:
            input_csv = sg.PopupGetFile('Select input CSV File', file_types=(("CSV Files", "*.csv"),), initial_folder=root_path)
            if input_csv is None:
                return None
            try:
                #dest_folder = create_folder(root_path, 'Shortest Path CSV')
                num_start = 10  # placeholder
                break
            except FileNotFoundError:
                sg.PopupError('Invalid file path')
        layout = [[sg.Text('Calculating shortest paths from CSV...\n(This may take a while)')],
                  [sg.ProgressBar(num_start, orientation='h', size=(20, 20), key='progress')]]
        window2 = sg.Window('Loading, Please wait...').Layout(layout)
        progress_bar = window2.FindElement('progress')
        mod_ref = 1 if num_start < 30 else (5 if num_start < 100 else num_start//10)
        for i in range(num_start):
            time.sleep(2)
            if i % (mod_ref) == 0:
                button, values = window2.Read(10)
                if values is None:
                    return None
                progress_bar.UpdateBar(i)
        window2.Close()
        sg.PopupOK("Shortest paths from CSV successful\nOutput CSV created")
    else:
        return None


def create_folder(root_path, new_folder):
    new_filepath = os.path.join(root_path, new_folder)
    if not os.path.exists(new_filepath):
        os.makedirs(new_filepath)
    return new_filepath


def condense_path(root_path):
    if len(root_path) > 50:
        display_path = root_path[:15] + '...' + root_path[-35:]
    else:
        display_path = root_path
    return display_path


def placeholder_db_foo(osm_filepath):
    time.sleep(3)
    pass


def placeholder_network_foo():
    time.sleep(5)
    pass


def exe_per_loop_foo(i):
    time.sleep(0.01)
    pass


def after_loop_foo():
    time.sleep(2)
    pass

def main():
    """
    Creates the UI window of the main menu window, which is persistent as long as the program is running
    """
    newNet = None
    db_name = 'from_osm_to.db'
    net_mod_cues = {'osm2db': '',
                    'network': 'Missing '+db_name+' \nin exe folder',
                    'shortest_path': 'No network data available'}

    menu_def = [['&File', ['Edit &Output Folder', '&Exit']],
                ['&Help', ['&About...']], ]

    text_size = (30, 1)
    cue_size1 = (21, 1)
    cue_size2 = (21, 2)
    network_col = [[sg.Text('Network Analysis', font=('Helvetica', 12))],
                   [sg.Text('1. Create database from OSM', size= text_size), sg.Button('Go', key='osm2db_go'), sg.Text('', key='osm2db_cue', text_color='grey', size= cue_size1)],
                   [sg.Text('2. Create network from database', size= text_size, pad=(5,0)), sg.Button('Go', key='network_go', disabled=True, pad=(5,0)), sg.Text('', key='network_cue', text_color='grey', size= cue_size2, pad=(5,0))],
                   [sg.Checkbox('Create shapefiles for network', key='net_shp_check', disabled=True, pad=(22, 0), default=True, text_color='OrangeRed3')],
                   [sg.Text('3. Calculate shortest path', size= text_size), sg.Button('Go', key='shortest_path_go', disabled=True), sg.Text(net_mod_cues['shortest_path'], key='shortest_path_cue', text_color='grey', size= cue_size1)]]
    root_path = ''
    layout = [[sg.Image(filename=os.path.join(src_path, 'logo.png'), key='image')],
              [sg.Menu(menu_def)],
              [sg.Column(network_col, pad=(0, 8))],
              [sg.Text('Output folder: ' + root_path, key='root_path_txt', size=(60, 1), font=('Helvetica', 10), text_color='grey', pad=(14, 8))],
              ]

    window = sg.Window('Sample GUI').Layout(layout)
    window.Finalize()
    if not os.path.isfile(db_name):
        window.FindElement('network_cue').Update(net_mod_cues['network'])
    else:
        window.FindElement('network_go').Update(disabled=False)
        window.FindElement('net_shp_check').Update(disabled=False)
    # ----------------- User chooses output folder -----------------
    while True:
        window.Enable()
        root_path = sg.PopupGetFolder('Choose output folder for Network Analysis', no_window=True)
        if root_path == '':
            window.Disable()
            sg.PopupOK('Please choose a output folder\n\nAll created output files will \nbe saved here', keep_on_top=True)
        else:
            break
    window.FindElement('root_path_txt').Update('Output folder: ' + condense_path(root_path))

    # ---------------- Actions from the main menu window -------------
    while True:
        button, values = window.Read()
        if button in [None, 'Exit']:
            print('terminate program')
            raise SystemExit
        elif button == 'Edit Output Folder':
            while True:
                new_root_path = sg.PopupGetFolder('Choose output folder for Network Analysis', no_window=True,
                                          keep_on_top=True, initial_folder=root_path)  # library issue: initial_folder isn't set here
                if new_root_path == '':
                    break
                else:
                    root_path = new_root_path
                    break
            window.FindElement('root_path_txt').Update('Output folder: ' + condense_path(root_path))
        elif button == 'osm2db_go':
            osm2db_success = False
            osm_filepath = import_osm_UI(root_path)
            if osm_filepath is None:
                continue
            while True:
                try:
                    assert os.path.isfile(osm_filepath)
                    layout = [[sg.Text('Creating database\nfrom OSM...')]]
                    window6 = sg.Window('Loading')
                    window6.Layout(layout).Read(timeout=10)
                    placeholder_db_foo(osm_filepath)
                    window6.Close()
                    osm2db_success = True
                    sg.PopupOK("Create database successful\nSaved as "+db_name)
                    window.FindElement('network_cue').Update('')
                    window.FindElement('network_go').Update(disabled=False)
                    window.FindElement('net_shp_check').Update(disabled=False)
                    break
                except AssertionError:
                    sg.PopupError('Please choose a valid \nOSM file')
                    osm_filepath = import_osm_UI(root_path, skip_check=True)
                except KeyError:
                    window6.Close()
                    layout = [[sg.Text('An error occurred.\n\nPlease try again or try a\ndifferent OSM file')],
                              [sg.Button('Try Again', pad=(5, 2)), sg.Button('Change OSM File')]]
                    window7 = sg.Window('Error loading OSM')
                    button, values = window7.Layout(layout).Read()
                    if button is None:
                        break
                    elif button == 'Try Again':
                        window7.Close()
                        continue
                    elif button == 'Change OSM File':
                        window7.Close()
                        osm_filepath = import_osm_UI(root_path, skip_check=True)
            if not osm2db_success:
                continue
        elif button == 'network_go':
            create_shpfiles = values['net_shp_check']
            selected_highway = select_highway_UI()
            if selected_highway is None:
                continue
            net_gen = create_network(newNet, selected_highway, root_path, create_shpfiles)
            if net_gen is None:
                continue
            sg.PopupOK("Network creation successful")
            window.FindElement('shortest_path_go').Update(disabled=False)
            window.FindElement('shortest_path_cue').Update('')
        elif button == 'shortest_path_go':
            if calculate_shortest_path(newNet, root_path) is None:
                continue
        elif button == 'About...':
            sg.Popup('This is the stripped demo software\n'
                     'for purpose of PySimpleGUI demo only\n')
        else:
            pass


if __name__ == '__main__':
    main()
    exit(69)
