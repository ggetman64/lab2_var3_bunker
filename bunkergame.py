# ============================================================
#   ЛАБОРАТОРНАЯ 2: КАРКАС БУНКЕРА + ФОНАРИК
#   Запуск игры:  python bunker.py
#   Запуск тестов: pytest bunker.py -v
# ============================================================

import random

class Item:
    def __init__(self, name):
        self.name = name

class Room:
    def __init__(self, name, desc, x, y):
        self.name = name
        self.desc = desc
        self.x = x
        self.y = y
        self.items = []

class PoweredDoor:
    def __init__(self):
        self.powered = False
        self.opened = False

class Player:
    def __init__(self):
        self.room = "airlock"  # Стартовая комната
        self.inventory = []
        self.battery = 100     # ЗАРЯД ФОНАРИКА

class Game:
    def __init__(self):
        self.player = Player()
        self.door = PoweredDoor()
        self.power_on = False
        self.code_entered = False

        # Создаем комнаты и задаем им координаты для карты
        self.rooms = {
            "storage":   Room("storage", "Склад с припасами.", 0, 0),
            "living":    Room("living", "Жилой блок. Пахнет пылью.", 1, 0),
            "airlock":   Room("airlock", "Шлюз. Вход в бункер.", 2, 0),
            "generator": Room("generator", "Генераторная. Тут есть рубильник.", 1, 1),
            "exit":      Room("exit", "Гермодверь на поверхность.", 2, 1),
            "command":   Room("command", "Командный пункт.", 1, 2)
        }
        
        # Раскладываем предметы (добавили 2 батарейки в склад)
        self.rooms["storage"].items.append(Item("батарейка"))
        self.rooms["storage"].items.append(Item("батарейка"))
        self.rooms["generator"].items.append(Item("switch"))
        self.rooms["command"].items.append(Item("записка"))
        
        # Карта переходов
        self.map = {
            "airlock": ["living", "exit"],
            "living": ["airlock", "storage", "generator"],
            "storage": ["living"],
            "generator": ["living", "command"],
            "command": ["generator"],
            "exit": ["airlock"]
        }

    # ---------- Отрисовка карты ----------
    def draw_map(self):
        W = 11
        border = "+" + ("-" * W + "+") * 3
        lines = [border]
        for row in range(3):
            line = "|"
            for col in range(3):
                found = None
                for r in self.rooms.values():
                    if r.x == col and r.y == row:
                        found = r
                        break
                
                if found is None:
                    inner = " " * W
                elif found.name == self.player.room:
                    inner = ("[" + found.name + "]").center(W)
                else:
                    inner = found.name.center(W)
                line += inner + "|"
            lines.append(line)
            lines.append(border)
        return "\n".join(lines)

    # ---------- Отрисовка экрана ----------
    def show_screen(self, message=""):
        print("\n" * 2)
        print("=" * 60)
        print(self.draw_map())
        print("=" * 60)
        
        r = self.rooms[self.player.room]
        print(f"Вы в комнате: {r.name.upper()} ({r.desc})")
        
        if r.items:
            print("Предметы здесь: " + ", ".join(i.name for i in r.items))
            
        if r.name == "exit":
            door_status = "ОТКРЫТА" if (self.power_on and self.code_entered) else "ЗАКРЫТА"
            print(f"Статус гермодвери: {door_status}")
            
        print("-" * 60)
        inv = ", ".join(i.name for i in self.player.inventory) if self.player.inventory else "пусто"
        power_str = "ВКЛ" if self.power_on else "выкл"
        
        # Выводим заряд фонарика в интерфейс
        print(f"Питание: {power_str} | Фонарик: {self.player.battery}% | Инвентарь: {inv}")
        print("-" * 60)
        
        if message:
            print(message)
            print("=" * 60)
            
        print("Команды: help | look | go <комната> | take <предмет> | use <предмет> | code <число> | exit")
        print("=" * 60)

    # ---------- Логика перехода ----------
    def move_to(self, arg):
        if arg not in self.map[self.player.room]:
            return "Нельзя туда пройти."
            
        if arg == "exit":
            if self.power_on and self.code_entered:
                return "WIN" # Специальный код победы
            else:
                return "Дверь заперта. Нужно включить питание и ввести код."
                
        # Проверка фонарика перед обычным переходом
        if self.player.battery < 10:
            return "Фонарик разряжен! Используйте батарейку, иначе вы не видите дорогу."
            
        self.player.battery -= 10
        self.player.room = arg
        msg = f"Вы перешли в комнату: {arg}. (Заряд: {self.player.battery}%)"
        
        # Случайное событие для атмосферы (20% шанс, что свет мигнет)
        if random.random() < 0.2:
            self.player.battery = max(0, self.player.battery - 10)
            msg += "\nСвет мигнул! Фонарик теряет заряд."
            
        return msg

    # ---------- Игровой цикл ----------
    def run(self):
        self.show_screen("ЦЕЛЬ: Включите питание, узнайте код и выйдите из бункера.")
        
        while True:
            cmd = input("> ").strip().lower()
            if not cmd:
                continue

            parts = cmd.split(maxsplit=1)
            verb = parts[0]
            arg = parts[1] if len(parts) > 1 else ""
            msg = ""

            if verb == "help":
                msg = "Доступные команды: help, look, go <комната>, take <предмет>, use <предмет>, code <число>, exit"

            elif verb == "look":
                msg = "Вы осмотрелись."

            elif verb == "go":
                msg = self.move_to(arg)
                if msg == "WIN":
                    self.show_screen("*** ПОБЕДА! Вы открыли гермодверь и вышли из бункера! ***")
                    break

            elif verb == "take":
                r = self.rooms[self.player.room]
                found = False
                for item in r.items:
                    if item.name == arg:
                        r.items.remove(item)
                        self.player.inventory.append(item)
                        msg = f"Вы взяли: {arg}."
                        found = True
                        break
                if not found:
                    msg = "Здесь нет такого предмета."

            elif verb == "use":
                if arg == "switch":
                    if self.player.room == "generator":
                        self.power_on = True
                        self.door.powered = True
                        msg = "Вы дёрнули рубильник. Питание включено!"
                    else:
                        msg = "Рубильник находится в генераторной."
                elif arg == "записка":
                    if self.player.room == "command" or "записка" in self.player.inventory:
                        msg = "В записке написано: КОД = 1234"
                    else:
                        msg = "У вас нет записки."
                
                # --- ИСПОЛЬЗОВАНИЕ БАТАРЕЙКИ ---
                elif arg == "батарейка":
                    # Сначала ищем в рюкзаке
                    if "батарейка" in self.player.inventory:
                        self.player.inventory.remove("батарейка")
                        self.player.battery = min(100, self.player.battery + 30)
                        msg = f"Батарейка использована. Заряд фонарика: {self.player.battery}%"
                    else:
                        # Если в рюкзаке нет, ищем на полу в комнате
                        r = self.rooms[self.player.room]
                        found = False
                        for item in r.items:
                            if item.name == "батарейка":
                                r.items.remove(item)
                                self.player.battery = min(100, self.player.battery + 30)
                                msg = f"Вы подобрали и использовали батарейку. Заряд: {self.player.battery}%"
                                found = True
                                break
                        if not found:
                            msg = "У вас нет батарейки."
                else:
                    msg = "Нельзя использовать этот предмет."

            elif verb == "code":
                if not arg.isdigit():
                    msg = "Ошибка: код должен состоять только из цифр!"
                elif arg == "1234":
                    self.code_entered = True
                    msg = "Код верный! Дверь разблокирована. Идите на exit."
                else:
                    msg = "Неверный код."

            elif verb == "exit":
                print("Вы вышли из игры. До встречи!")
                break

            else:
                msg = "Некорректная команда. Введите help."

            self.show_screen(msg)
            
            # --- ПРОВЕРКА НА ПРОИГРЫШ ---
            # Если заряд < 10 и нет батареек под рукой, игрок застревает
            if self.player.battery < 10:
                has_bat = "батарейка" in self.player.inventory
                for item in self.rooms[self.player.room].items:
                    if item.name == "батарейка":
                        has_bat = True
                if not has_bat and self.player.room != "exit":
                    self.show_screen("Фонарик окончательно сел. Вы остались в темноте... ИГРА ПРОИГРАНА.")
                    break


# ============================ ТЕСТЫ ============================

def test_start_room():
    g = Game()
    assert g.player.room == "airlock"
    assert g.player.battery == 100 # Фонарик полный

def test_switch_power():
    g = Game()
    assert g.power_on == False
    g.power_on = True 
    assert g.power_on == True

def test_code_is_number():
    assert "1234".isdigit()
    assert not "abcd".isdigit()

def test_battery_mechanic():
    g = Game()
    g.player.room = "airlock"
    g.move_to("living") # Идем в жилой блок
    assert g.player.battery <= 90 # Заряд списался

def test_win_condition():
    g = Game()
    g.power_on = True
    g.code_entered = True
    assert (g.power_on and g.code_entered) == True


# ============================ ЗАПУСК ============================
if __name__ == "__main__":
    Game().run()