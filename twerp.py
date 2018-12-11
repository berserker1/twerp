import os
import sys
path = os.path.abspath(os.path.dirname(__file__))
PATH_TO_MODULE=os.path.join(path,'wiki_files')
sys.path.append(PATH_TO_MODULE)


import pywikibot
from pywikibot import pagegenerators
import string

from course_details import getDeptList,getCourseData,getCoursesDeptWise
from time_table_to_wiki_table import getTimeTable
from add_timetable_to_wiki import create_course_page, update_with_timetable, update_without_timetable
from prof_details import get_all_info_of_faculty,get_table_of_prof
from update_prof_table import check_profpage_existence, create_prof_page,make_Time_Table_of_prof, update_profpage_with_timetable

site = pywikibot.Site()

def course_department_wise(allcoursesonwiki,existing_course_pages):
    departments = getDeptList()
    course_list_this_sem = []
    new_pages_created = []

    for department in departments:
        print('Courses from ' + department['name'] )
        courses = getCoursesDeptWise(department['code'])
        for course in courses:
            if course['code'] == 'EA10005':
                continue

            course['name'] = string.capwords(course['name'])
            if course['code'] not in existing_course_pages:
                new_pages_created.append(course['code'])
                course['department'] = department['name']
                timetable = getTimeTable(getCourseData(course))
                create_course_page(site,course,timetable)
            else:
                timetable = getTimeTable(getCourseData(course))
                update_with_timetable(allcoursesonwiki,site,course,timetable)

            course_list_this_sem.append(course['code'])

    print('\n\nFound ' + str(len(course_list_this_sem)) + ' courses being offered this semester')
    not_this_sem_courses  = [i for i in allcoursesonwiki if i not in course_list_this_sem]


    print('Now removing previous year\'s timetable from the courses not in this semester')
    for course in not_this_sem_courses:
        print(allcoursesonwiki[course])
        update_without_timetable(allcoursesonwiki,site,course)

    print('New pages Created = ' + str(len(new_pages_created)))
    print('Courses this semester = ' + str(len(course_list_this_sem)))
    print("\n")


#      TODO : WRITE THE NAME OF THE CURRENT SEM AS HEADING TO THE TIMETABLE
def update_time_table_of_prof():
    info_table=get_all_info_of_faculty()
    for entry in info_table:
        table_json=get_table_of_prof(entry['name'],entry['department']['code'])
        timetable=make_Time_Table_of_prof(table_json)
        prof_existence=check_profpage_existence(entry['name'])
        if(prof_existence==1):#1 means not exist
            print("Page of professor {} not found ".format(entry['name']))
            create_prof_page(entry,site,timetable)
        else:
            print('Professor {} page found'.format(entry['name']))
            update_profpage_with_timetable(entry,site,timetable)
        print("Updated time table of {}".format(entry['name']))

def main():

    cat = pywikibot.Category(site,'Category:Courses')
    gen = pagegenerators.CategorizedPageGenerator(cat)

    allcoursesonwiki = {i.title()[:7]:i for i in gen}

    existing_course_pages = []
    for keys in allcoursesonwiki:
        existing_course_pages.append(keys)

    course_department_wise(allcoursesonwiki,existing_course_pages)
    print('Starting to update prof pages')    
    update_time_table_of_prof()

if __name__ == '__main__':
    main()