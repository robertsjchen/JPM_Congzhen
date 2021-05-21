# coding: utf-8
# process_koreader: add some "<span class='xx'>" for kobo ereader
import os
import sys

def list_folders_files(path, suffixes_filters = []):
    list_folders = []
    list_files = []
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isdir(file_path):
            list_folders.append(file)
        else:
            file_ext = os.path.splitext(file)[-1]
            ignore_this_file = 0
            if (suffixes_filters is not None):
                ignore_this_file = 1
                for suffix in suffixes_filters:
                    if (file_ext.upper() == suffix.upper()):
                        ignore_this_file = 0
                        break
            if (ignore_this_file == 0):
                list_files.append(file)
    return (list_folders, list_files)

added_span_flg = 0
def processParagraph(input_line_buff, output_buff_array):    
    '''
    add additional <span> for kobo reader
    '''
    global added_span_flg
    
    index2 = -1
    index1 = input_line_buff.find('<p', 0)
    if (index1 >= 0):
        index2 = input_line_buff.find('>', index1 + 2)
    if ((index1 < 0) or (index2 < 0)):
        output_buff_array.append(input_line_buff)
        return
    
    key_classes = ['poem', 'pz', 'poetry', 'poetry_right', 'poetry_no_intent']
    for class_name in key_classes:
        # <p class="shi">
        class_name_full = 'class=' + '\"' + class_name + '\"'
        index3 = input_line_buff.find(class_name_full, index1, index2)
        index4 = -1
        if (index3 > 0):
            index4 = input_line_buff.find('</p>', index2)

        if (index3 > 0):
            # <p class="shi">
            output_buff_array.append(input_line_buff[:(index2 + 1)])

            # <span class="content_kt">
            output_buff_array.append('<span ' + 'class=\"content_kt\"' + '>')
            # output_buff_array.append('<span ' + class_name_full + '>')

            if (index4 > 0):
                added_span_flg = 0
                
                # append content:
                output_buff_array.append(input_line_buff[(index2 + 1) : index4])

                output_buff_array.append('</span>')
                output_buff_array.append('</p>' + '\n')
                return
            else:
                output_buff_array.append(input_line_buff[(index2 + 1) : ])
                added_span_flg = 1
                
                # print('-->' + input_line_buff[(index2 + 1) : ])
                return

    # just copy original content:
    output_buff_array.append(input_line_buff)

def processLine(input_line_buff, output_buff_array):
    if (len(input_line_buff) <= 0):
        return

    global added_span_flg
    find_index = input_line_buff.find('<p', 0)
    if (find_index < 0):
        # no <p xxx> found
        if (added_span_flg != 0):
            index2 = input_line_buff.find('</p>')
            if (index2 >= 0):
                # print ('-->' + input_line_buff)
                output_buff_array.append(input_line_buff[0 : index2])
                output_buff_array.append('</span>')
                output_buff_array.append('</p>\n')
                added_span_flg = 0
                return
            
        
        # nothing to do
        output_buff_array.append(input_line_buff)
        return

    processParagraph(input_line_buff, output_buff_array)

def processFile2(path_i, fileName):
    global added_span_flg
    
    added_span_flg = 0
    
    full_path = os.path.join(path_i, fileName)
    # print(full_path)
    print(fileName)

    global is_normal_chapter
    global chapter_count
    global split_count

    tmp_str = ''

    is_normal_chapter = False

    outputLineBuff = []
    with open(full_path, 'rt') as file:
        tmp_str = fileName + ": "

        for line_string in file:
            if (len(line_string) <= 2):
                outputLineBuff.append(line_string);
                continue

            outputLineBuff2 = []
            processLine(line_string, outputLineBuff2)

            line_buf = ''.join(outputLineBuff2)
            if (len(line_buf) <= 1):
                continue;

            outputLineBuff.append(line_buf)

    if (len(outputLineBuff) < 1):
        return

    output_folder = './out'
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    target_file = os.path.join(output_folder, fileName)
    with open(target_file, 'wt') as file:
        for line_buff in outputLineBuff:
            file.write(line_buff)

if __name__ == '__main__':
    # batRename(sys.argv)
    suffixes_filters = []

    suffixes_filters.append(".html")
    (list_folders, list_files) = list_folders_files('./text', suffixes_filters)
    print("files: %d" % len(list_files))

    for item in sorted(list_files):
        processFile2('./text', item)
