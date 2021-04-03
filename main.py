from custom_exceptions import UserExitException
from models import (Storage, Question, TestResults, MainMenu, TestMenu, EditMenu)
import json
import pymysql # ignore that


# ==================================================================================================
# App storage

def fill_storage():
    """
    Transfers the data from permanent storage in wsl's database to temporary storage in Storage() instance.
    """

    storage = Storage()
    
    try:
        with storage.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM question_data")
            q_data = cursor.fetchall()
            cursor.execute("SELECT * FROM question_answers")
            ans_data = cursor.fetchall()
            

            for q_obj in q_data:
                try:
                    cur_answers = [ans['answer_text'] for ans in ans_data if ans['id'] == q_obj['id']]

                    item = Question(q_obj['id'], q_obj['text'], cur_answers, q_obj['c_answered'], q_obj['w_answered'])
                    # print(f'- {item.id} - {item.text} - {item.answers} - {item.c_answered} - {item.w_answered}')
                    storage.questions.append(item)
                except KeyError:
                    pass

    except Exception as ex:
        print(f'Database connection error:', ex)

            

def fill_database():
    """
    Transfers the edited data from temporary storage in Storage() instance to permanent storage in wsl's database.
    """

    storage = Storage()

    try:
        with storage.connection.cursor() as cursor:
            cursor.execute("DELETE FROM question_answers WHERE TRUE")
            cursor.execute("DELETE FROM question_data WHERE TRUE")

            # print('\nInserting values into question_data:')
            for question in storage.questions:
                query = f"INSERT INTO question_data VALUES ({question.id}, \'{question.text}\', {question.c_answered}, {question.w_answered});"
                # print('\n', query)
                cursor.execute(query)

                # print(f'\n\tInserting question\'s values into question_answers:')
                for ans in question.answers:
                    query1 = f"INSERT INTO question_answers VALUES ({question.id}, \'{ans}\')"
                    # print('\t', query1)
                    cursor.execute(query1) 
                
            storage.connection.commit()

    except Exception as ex:
        print(f'Database connection error:', ex)



def save_test_results(updated_questions):
    """
    Updates the data stored in temporare storage of Storage()'s instance after the test.
    """
    
    storage = Storage()

    for updated_q in updated_questions:
        for stored_q in storage.questions:
            if stored_q.id == updated_q.id:
                stored_q.c_answered = updated_q.c_answered
                stored_q.w_answered = updated_q.w_answered


def save_edit_results(updated_questions):
    """
    Updates the data stored in temporare storage of Storage()'s instance after the editing of questions.
    """
    
    storage = Storage()
    storage.questions = updated_questions


# ==================================================================================================
# App assembly

def menu_logic(mode, m_menu, t_menu, e_menu):
    if mode == 'main':
        mode = m_menu.user_id_input()
        return mode
    elif mode == 'test':
        result_list = t_menu.test_logic()
        
        save_test_results(result_list[0])
        result_menu = TestResults(*result_list)
        
        mode = result_menu.user_id_input()
        return mode
    elif mode == 'edit':
        save_edit_results(e_menu.edit_logic())
        return 'main'
    elif mode == 'exit':
        raise UserExitException()

    

def main():
    fill_storage()
    
    main_menu = MainMenu()
    test_menu = TestMenu()
    edit_menu = EditMenu()
    
    mode = 'main'
    
    while True:
        try:
            mode = menu_logic(mode, main_menu, test_menu, edit_menu)
        except UserExitException:
            print('\n\n=================================================\nExiting the programm; saving the data.\nThank you for using this software and goodbye!')
            fill_database()
            storage = Storage()
            storage.close_db_connection()        
            exit(0)



if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n\n=================================================\nForced programm shutdown; saving the data.\nThank you for using this software and goodbye!')
        fill_database()
        storage = Storage()
        storage.close_db_connection()



