from input_utils import (get_input_function, get_num_input_function)
from custom_exceptions import (UserExitException, UserInputTextException, UserInputNumException)
import random
import pymysql # ignore that


# ==================================================================================================
# Bases:

class Option:
    def __init__(self, id, title, mode):
        self.id = id
        self.title = title
        self.mode = mode



class BaseMenu:
    def __init__(self, title, options):
        self.title = title
        self.options = options


    def show(self):
        print('\n---------------', self.title, '---------------')
        for option in self.options:
            print(f'[{option.id}] - {option.title}')


    def user_id_input(self):
        input_func = get_num_input_function()

        while True:
            try:
                self.show()
                input_id = input_func('\nEnter option\'s id: ')
                mode = self.options[int(input_id) - 1].mode
                break
            except (UserInputNumException, ValueError):
                print(f'\n>>> Invalid input; enter a number from {self.options[0].id} to {self.options[-1].id}. <<<')          
            except IndexError:
                print(f'\n>>> Index {input_id} doesn\'t exist; input a number from {self.options[0].id} to {self.options[-1].id}. <<<')
              
        return mode


    def user_text_input(self, string):
        input_func = get_input_function()

        def get_text(string):
            while True:
                try:
                    input_text = input_func(string)
                    return input_text
                except UserInputTextException:
                    print(f'\n>>> Invalid input; some of inputted symbols are not recognized by programm. <<<')

        text = get_text(string)
        return text


# ==================================================================================================
# Menus:

class MainMenu(BaseMenu):
    menu_options = (
        Option('1', 'Start Test', 'test'),
        Option('2', 'Edit Test', 'edit'),
        Option('3', 'Exit', 'exit')
    )
    
    def __init__(self):
        super().__init__('Main Menu', self.menu_options)



class TestMenu(BaseMenu):
    menu_options = (
        Option('1', 'Continue', 'stay'),
        Option('2', 'Back', 'main')
    )

    def __init__(self):
        super().__init__('Test Menu', self.menu_options)
        self.test_results = []


    def test_logic(self):
        storage = Storage()
        questions_left = storage.questions.copy()
        ans_questions = []
        overall_cor_ans = 0

        if len(storage.questions) != 0:
            for i in range(len(questions_left)):     
                cur_question = questions_left.pop(questions_left.index(random.choice(questions_left))) # old version: cur_question = questions_left.pop(random.choice([i1 for i1 in range(len(questions_left))])) 
                
                print('\n---------------', self.title, '---------------')
                print(f'{i+1}.', cur_question)

                if self.user_text_input(f'\nEnter your answer here: ').lower() in [i.lower() for i in cur_question.answers]:
                    cur_question.c_answered += 1
                    overall_cor_ans += 1
                else:
                    cur_question.w_answered += 1

                ans_questions.append(cur_question)

                if self.user_id_input() == 'main':
                    break      
        return (ans_questions, overall_cor_ans)
            


class TestResults(BaseMenu):
    menu_options = (
        Option('1', 'Retry test', 'test'),
        Option('2', 'Back to main menu', 'main')
    )

    def __init__(self, ans_questions, cor_ans):
        super().__init__('Test results', self.menu_options)
        self.ans_questions = ans_questions
        self.cor_ans = cor_ans


    def show(self):
        questions = len(self.ans_questions)
        
        print('\n---------------', self.title, '---------------')
        print(f'You\'ve answered correctly on {self.cor_ans} out of {questions} questions.', end=' ')

        if self.cor_ans <= questions:
            if self.cor_ans <= (questions / 3) * 2:
                if self.cor_ans <= questions / 3:
                    print('Better luck next time!\n')
                else:
                    print('Good work!\n')
            else:
                print('Excellent!\n')
        
        for option in self.options:
            print(f'[{option.id}] - {option.title}')



class EditMenu(BaseMenu):   
    menu_options = (
        Option('1', 'Select question', 'q_sel'),
        Option('2', 'Add question', 'q_add'),
        Option('3', 'Back', 'back')
    )
    
    def __init__(self):
        super().__init__('Edit Menu', self.menu_options)
        self.storage = Storage()
     

    def edit_answers(self):
        result = []
        cur_segment = ''
        
        for i in self.user_text_input('Enter question\'s answers (separate them by \';\' symbol): '):
            if i != ';':
                if i == ' ' and cur_segment == '':
                    pass
                else:
                    cur_segment = cur_segment + i
            else:
                result.append(cur_segment)
                cur_segment = ''
        
        result.append(cur_segment)

        return result


    def add_question(self, questions):
        question_text = self.user_text_input('\nEnter question\'s text: ')
        question_answers = self.edit_answers()
        available_ids = [i for i in range(10000)]
        for i in questions:
            try:
                available_ids.remove(i.id)
            except ValueError:
                pass
        confirmation = self.user_text_input('Please, enter any key to confirm (\'#\' to cancel): ')
        
        if confirmation != '#':
            new_q = Question(random.choice(available_ids), question_text, question_answers, 0, 0)
            questions.append(new_q)


    def select_question(self, questions):
        option_list = (*questions, 'back')

        def get_selection():
            input_func = get_num_input_function()

            while True:
                try:
                    print('\n---------------', self.title, '---------------')
                    for i in range(len(option_list) - 1):
                        print(f'[{i+1}] - Edit question №{option_list[i].id}: "{option_list[i].text}"')
                    print(f'[{len(option_list)}] - Back to edit menu')
                    
                    user_input = int(input_func('\nEnter option\'s id: '))
                    selected = option_list[user_input - 1]
                    return selected
                except (UserInputNumException, ValueError):
                    print(f'\n>>> Invalid input; enter a number from 1 to {len(option_list)}. <<<')   
                except IndexError:
                    print(f'\n>>> Index {user_input} doesn\'t exist; input a number from 1 to {len(option_list)}. <<<')

        selected = get_selection()
        return selected
            

    def edit_logic(self):
        question_list = self.storage.questions.copy()

        while True:
            edit_mode = self.user_id_input()
            
            if edit_mode == 'q_sel':
                selected = self.select_question(question_list) 
                if selected != 'back':
                    question_edit = QuestionEditMenu(selected, question_list)
                    question_list = question_edit.q_editing_logic()
            
            elif edit_mode == 'q_add':
                self.add_question(question_list)

            elif edit_mode == 'back':
                return question_list



class QuestionEditMenu(EditMenu):
    menu_options = (
        Option('1', 'Edit question\'s text', 'e_text'),
        Option('2', 'Edit question\'s answers', 'e_ans'),
        Option('3', 'Withdraw question\'s stats', 'w_stats'),
        Option('4', 'Delete question', 'del'),
        Option('5', 'Finish editing the question', 'back'),
    )

    def __init__(self, question, questions):
        super().__init__()
        self.questions = questions
        self.question = question
     

    def show(self):
        print('\n---------------', self.title, '---------------')
        print(f'Question №{self.question.id}:\ntext - "{self.question.text}",\nanswers - {self.question.answers},\nstatistics - correct: {self.question.c_answered}, wrong: {self.question.w_answered}\n')
        for option in self.options:
            print(f'[{option.id}] - {option.title}')


    def q_editing_logic(self):
        try:
            selected_question = self.questions[self.questions.index(self.question)]

            while True:
                action = self.user_id_input()

                if action == 'e_text':
                    selected_question.text = self.user_text_input(f'Enter question\'s new text: ')
                
                elif action == 'e_ans':
                    selected_question.answers = self.edit_answers()
                
                elif action == 'w_stats':
                    selected_question.c_answered = 0
                    selected_question.w_answered = 0
                
                elif action == 'del':
                    while True:
                        confirmation = self.user_text_input('\nAre you sure? (y/n) ')
                        if confirmation == 'y':
                            self.questions.pop(self.questions.index(self.question))
                            return self.questions
                        elif confirmation == 'n':
                            break
                        else:
                            print('User must input \'y\' symbol as "yes" and \'n\' symbol as "no"')

                elif action == 'back':
                    return self.questions
        except (KeyboardInterrupt, UserExitException):
            storage = Storage()
            storage.questions = self.questions
            raise UserExitException

# ==================================================================================================
# Other:

class Storage:
    instance = None
    questions = None
    connection = None
    
    @staticmethod
    def get_db_connection():
        connection = pymysql.connect(
            host='127.0.0.1',
            user='my_user',
            password='3212#Moya3212',
            db='test_app_storage',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        return connection


    @classmethod
    def close_db_connection(cls):
        try:
            cls.connection.close()
            print('\nDatabase connection was closed successfuly!\n')
        except Exception as ex:
            print('\nFailed to close connection with database:', ex, '\n')


    @classmethod
    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = object.__new__(cls)
            cls.questions = []
            cls.connection = cls.get_db_connection()
        return cls.instance



class Question:
    def __init__(self, id, text, answers, c_answered, w_answered):
        self.id = id
        self.text = text
        self.answers = answers
        self.c_answered = c_answered
        self.w_answered = w_answered


    def __str__(self):
        return f'{self.text} Correct answers - {len(self.answers)}.'
        



