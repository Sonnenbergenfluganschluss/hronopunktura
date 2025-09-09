# Добро пожаловать на первый этап твоей стажировки!

И вот инструкции на предстоящую неделю ↓

Первый спринт нашего проекта посвящён оценке ориентации человека в графическом формате (Human Pose Skeleton).

По сути, это набор координат, которые можно связать для описания позы человека (освежить тему в памяти можно тут). Каждая координата в скелете — это ключевая точка (key point). Правильное соединение между двумя частями называется ветвью (limb).

img
Итак, в качестве первого шага к созданию виртуального коуча тебе необходимо определить ключевые точки спортсмена на фото и на их основе построить каркас позы человека, а именно осуществить следующую цепочку преобразований изображения бегущей девушки.

Нажмите на изображение, чтобы открыть его в полном размере ↓


Как это сделать? Сейчас будем разбираться!




# Спринт I: построение каркаса позы через ключевые точки
Для создания Human Pose Skeleton можно воспользоваться архитектурой Keypoint RCNN, имплементация которой представлена в библиотеке torchvision.

Модель обучена на наборе данных MS-COCO (Common Objects in Context) с целью обнаружения 17 ключевых точек человеческого тела (нос, глаза, уши, плечи, локти, запястья, бёдра, колени и лодыжки).

Архитектура Keypoint RCNN представлена на рисунке ниже.

img
Источник изображения
img
Модель выводит список из следующих элементов:

- boxes — тензор размера [N, 4], где N — количество обнаруженных объектов.
- labels — тензор размера [N], класс объекта. Он всегда равен 1, так как каждый обнаруженный «ящик» указывает на человека. 0 обозначает фоновый класс.
- scores — тензор размера [N], отображающий показатель достоверности обнаруженного объекта.
- keypoints — тензор размера [N, 17, 3], отображающий 17 ключевых точек N человек. Первые два числа — координаты x и y, а третье — видимость.
- keypoints_scores — тензор размера [N, 17], отражающий оценку всех ключевых точек для каждого обнаруженного человека.

Keypoint RCNN имеет готовую реализацию в обёртке PyTorch. С помощью данной модели мы без труда детектируем ключевые точки человеческого тела (от глаз до лодыжек) на изображении, а также получаем степень достоверности этих обнаружений.

Нам предстоит воспользоваться уже обученной сетью для отрисовки каркаса бегущей девушки.

Аутсорсный CV-инженер успел частично подготовить для нас перечень шагов, необходимых для отрисовки каркаса человека.

Наша задача — воспроизвести готовые и дописать пропущенные части кода.

1. Загрузи предобученную сеть torchvision.models.detection.keypointrcnn_resnet50_fpn и подготовь её для инференса.

2. Создай список опорных точек:

```python
keypoints = ['nose','left_eye','right_eye',\
'left_ear','right_ear','left_shoulder',\
'right_shoulder','left_elbow','right_elbow',\
'left_wrist','right_wrist','left_hip',\
'right_hip','left_knee', 'right_knee', \
'left_ankle','right_ankle']
```
3. Загрузи и примени трансформации transforms.Compose([T.ToTensor()]) к изображению бегущей девушки.

<img src='https://lms-cdn.skillfactory.ru/assets/courseware/v1/916f2b30ed417a727ebf512c413d20dd/asset-v1:SkillFactory+DSPR-CV+ALWAYS+type@asset+block/dspr_cv_u1_diploma_spr1_3_1.png'>

4. Прогони изображение через модель для получения ключевых точек.

5. Отрисуй ключевые точки с помощью функции draw_keypoints_per_person:

```python
def draw_keypoints_per_person(img, all_keypoints, all_scores, confs,           keypoint_threshold=2, conf_threshold=0.9):
    # создаём спектр цветов
    cmap = plt.get_cmap("rainbow")
    # создаём копию изображений
    img_copy = img.copy()
    color_id = np.arange(1, 255, 255 // len(all_keypoints)).tolist()[::-1]
    # для каждого задетектированного человека
    for person_id in range(len(all_keypoints)):
        # проверяем степень уверенности детектора
        if confs[person_id] > conf_threshold:
            # собираем ключевые точки конкретного человека
            keypoints = all_keypoints[person_id, ...]
            # собираем скоры для ключевых точек
            scores = all_scores[person_id, ...]
            # итерируем по каждому скору
            for kp in range(len(scores)):
                # проверяем степень уверенности детектора опорной точки
                if scores[kp] > keypoint_threshold:
                    # конвертируем массив ключевых точек в список целых чисел
                    keypoint = tuple(
                        map(int, keypoints[kp, :2].detach().numpy().tolist())
                    )
                    # выбираем цвет
                    color = tuple(np.asarray(cmap(color_id[person_id])[:-1]) * 255)
                    # рисуем кружок радиуса 5 вокруг точки
                    cv2.circle(img_copy, keypoint, 5, color, -1)

    return img_copy
```
6. Используя вспомогательную функцию, создай список «конечностей» девушки:

```python
def get_limbs_from_keypoints(keypoints):
    limbs = [
        [keypoints.index("right_eye"), keypoints.index("nose")],
        [keypoints.index("right_eye"), keypoints.index("right_ear")],
        [keypoints.index("left_eye"), keypoints.index("nose")],
        [keypoints.index("left_eye"), keypoints.index("left_ear")],
        [keypoints.index("right_shoulder"), keypoints.index("right_elbow")],
        [keypoints.index("right_elbow"), keypoints.index("right_wrist")],
        [keypoints.index("left_shoulder"), keypoints.index("left_elbow")],
        [keypoints.index("left_elbow"), keypoints.index("left_wrist")],
        [keypoints.index("right_hip"), keypoints.index("right_knee")],
        [keypoints.index("right_knee"), keypoints.index("right_ankle")],
        [keypoints.index("left_hip"), keypoints.index("left_knee")],
        [keypoints.index("left_knee"), keypoints.index("left_ankle")],
        [keypoints.index("right_shoulder"), keypoints.index("left_shoulder")],
        [keypoints.index("right_hip"), keypoints.index("left_hip")],
        [keypoints.index("right_shoulder"), keypoints.index("right_hip")],
        [keypoints.index("left_shoulder"), keypoints.index("left_hip")],
    ]
    return limbs


limbs = get_limbs_from_keypoints(keypoints)
```

7. Создай функцию для отрисовки каркаса (скелета) на базе уже имеющейся функции отрисовки ключевых точек.

8. Отрисуй каркас на изображении.

9. Сохрани получившийся ноутбук — он пригодится тебе в следующих спринтах.

Отлично! У тебя всё получилось, и теперь ты умеешь определять каркас человека по фото.

Для того чтобы создать виртуального коуча, также надо научиться сравнивать полученную позу с референсной.

О том, какие метрики помогут справиться с этой задачей и как это поможет нашему коучу, тимлид расскажет тебе в следующем спринте!

Предыдущий спринт помог тебе разобраться, как отрисовывать скелет человека по опорным точкам. Из исходного изображения бегущей спортсменки ты получил подобную картинку:

img
Для этого ты самостоятельно написал функцию отрисовки скелета. Давай сверим её с нашим вариантом draw_skeleton_per_person().

img
Функция draw_skeleton_per_person() принимает на вход изображение img, ключевые точки all_keypoints, оценку всех ключевых точек для каждого обнаруженного человека all_scores, показатель достоверности обнаруженных объектов confs, а также пороги keypoint_threshold и conf_threshold.

def draw_skeleton_per_person(img, all_keypoints, all_scores, confs, keypoint_threshold=2, conf_threshold=0.9):
# Для каждого найденного человека:
# проверяем степень уверенности детектора confs[person_id]
if confs[person_id] > conf_threshold:
	# собираем опорные точки конкретного человека
	# для каждой ветви (пары опорных точек):
				# выбираем первоначальную точку конечности 1 и 2
				# считаем limb_score как минимальную оценку ключевой точки среди двух оценок ключевых точек
				# проверяем, превосходит ли скор конечностей порог
				if limb_score> keypoint_threshold:
					# рисуем линию
Полный вариант решения ты найдёшь в ноутбуке. 

Для получения каркаса человека также можно использовать другие подходы, например OpenPose.