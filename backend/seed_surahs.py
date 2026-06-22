from backend.database import SessionLocal, engine
from backend import models

# Partial list for example; in production, this should contain all 114
SURAH_DATA = [ # (id, name, total_ayahs, start_page, end_page) - Page numbers are approximate for a 604-page Mushaf
    (1, "Al-Fatiha", 7, 1, 1), # Juz 1
    (2, "Al-Baqarah", 286, 2, 49), # Juz 1-3
    (3, "Al-Imran", 200, 50, 76), # Juz 3-4
    (4, "An-Nisa", 176, 77, 106), # Juz 4-6
    (5, "Al-Ma'idah", 120, 106, 127), # Juz 6-7
    (6, "Al-An'am", 165, 128, 150), # Juz 7-8
    (7, "Al-A'raf", 206, 151, 176), # Juz 8-9
    (8, "Al-Anfal", 75, 177, 186), # Juz 9-10
    (9, "At-Tawbah", 129, 187, 207), # Juz 10-11
    (10, "Yunus", 109, 208, 221), # Juz 11
    (11, "Hud", 123, 221, 235), # Juz 11-12
    (12, "Yusuf", 111, 235, 248), # Juz 12-13
    (13, "Ar-Ra'd", 43, 249, 255), # Juz 13
    (14, "Ibrahim", 52, 255, 261), # Juz 13
    (15, "Al-Hijr", 99, 262, 267), # Juz 14
    (16, "An-Nahl", 128, 267, 281), # Juz 14
    (17, "Al-Isra", 111, 282, 293), # Juz 15
    (18, "Al-Kahf", 110, 293, 304), # Juz 15-16
    (19, "Maryam", 98, 305, 312), # Juz 16
    (20, "Taha", 135, 312, 321), # Juz 16
    (21, "Al-Anbiya", 112, 322, 331), # Juz 17
    (22, "Al-Hajj", 78, 332, 341), # Juz 17
    (23, "Al-Mu'minun", 118, 342, 349), # Juz 18
    (24, "An-Nur", 64, 350, 359), # Juz 18
    (25, "Al-Furqan", 77, 359, 366), # Juz 19
    (26, "Ash-Shu'ara", 227, 367, 376), # Juz 19
    (27, "An-Naml", 93, 377, 384), # Juz 19-20
    (28, "Al-Qasas", 88, 385, 396), # Juz 20
    (29, "Al-Ankabut", 69, 396, 404), # Juz 20-21
    (30, "Ar-Rum", 60, 404, 410), # Juz 21
    (31, "Luqman", 34, 411, 414), # Juz 21
    (32, "As-Sajdah", 30, 414, 417), # Juz 21
    (33, "Al-Ahzab", 73, 418, 427), # Juz 21-22
    (34, "Saba", 54, 428, 434), # Juz 22
    (35, "Fatir", 45, 434, 440), # Juz 22
    (36, "Ya-Sin", 83, 440, 445), # Juz 22-23
    (37, "As-Saffat", 182, 446, 452), # Juz 23
    (38, "Sad", 88, 453, 458), # Juz 23
    (39, "Az-Zumar", 75, 458, 467), # Juz 23-24
    (40, "Ghafir", 85, 467, 476), # Juz 24
    (41, "Fussilat", 54, 477, 482), # Juz 24-25
    (42, "Ash-Shura", 53, 483, 489), # Juz 25
    (43, "Az-Zukhruf", 89, 489, 495), # Juz 25
    (44, "Ad-Dukhan", 59, 496, 498), # Juz 25
    (45, "Al-Jathiyah", 37, 499, 502), # Juz 25
    (46, "Al-Ahqaf", 35, 502, 506), # Juz 26
    (47, "Muhammad", 38, 507, 510), # Juz 26
    (48, "Al-Fath", 29, 510, 515), # Juz 26
    (49, "Al-Hujurat", 18, 515, 517), # Juz 26
    (50, "Qaf", 45, 518, 520), # Juz 26
    (51, "Adh-Dhariyat", 60, 520, 523), # Juz 26-27
    (52, "At-Tur", 49, 523, 525), # Juz 27
    (53, "An-Najm", 62, 526, 528), # Juz 27
    (54, "Al-Qamar", 55, 528, 531), # Juz 27
    (55, "Ar-Rahman", 78, 531, 534), # Juz 27
    (56, "Al-Waqi'ah", 96, 534, 537), # Juz 27
    (57, "Al-Hadid", 29, 537, 541), # Juz 27
    (58, "Al-Mujadila", 22, 542, 545), # Juz 28
    (59, "Al-Hashr", 24, 545, 548), # Juz 28
    (60, "Al-Mumtahanah", 13, 549, 551), # Juz 28
    (61, "As-Saff", 14, 551, 552), # Juz 28
    (62, "Al-Jumu'ah", 11, 553, 553), # Juz 28
    (63, "Al-Munafiqun", 11, 554, 554), # Juz 28
    (64, "At-Taghabun", 18, 555, 556), # Juz 28
    (65, "At-Talaq", 12, 556, 558), # Juz 28
    (66, "At-Tahrim", 12, 558, 560), # Juz 28
    (67, "Al-Mulk", 30, 562, 564), # Juz 29
    (68, "Al-Qalam", 52, 564, 566), # Juz 29
    (69, "Al-Haqqah", 52, 566, 568), # Juz 29
    (70, "Al-Ma'arij", 44, 568, 570), # Juz 29
    (71, "Nuh", 28, 570, 571), # Juz 29
    (72, "Al-Jinn", 28, 572, 573), # Juz 29
    (73, "Al-Muzzammil", 20, 574, 575), # Juz 29
    (74, "Al-Muddaththir", 56, 575, 577), # Juz 29
    (75, "Al-Qiyamah", 40, 577, 578), # Juz 29
    (76, "Al-Insan", 31, 578, 580), # Juz 29
    (77, "Al-Mursalat", 50, 580, 581), # Juz 29
    (78, "An-Naba", 40, 582, 583), # Juz 30
    (79, "An-Nazi'at", 46, 583, 584), # Juz 30
    (80, "Abasa", 42, 585, 585), # Juz 30
    (81, "At-Takwir", 29, 586, 586), # Juz 30
    (82, "Al-Infitar", 19, 587, 587), # Juz 30
    (83, "Al-Mutaffifin", 36, 587, 589), # Juz 30
    (84, "Al-Inshiqaq", 25, 589, 589), # Juz 30
    (85, "Al-Buruj", 22, 590, 590), # Juz 30
    (86, "At-Tariq", 17, 591, 591), # Juz 30
    (87, "Al-A'la", 19, 591, 592), # Juz 30
    (88, "Al-Ghashiyah", 26, 592, 593), # Juz 30
    (89, "Al-Fajr", 30, 593, 594), # Juz 30
    (90, "Al-Balad", 20, 594, 595), # Juz 30
    (91, "Ash-Shams", 15, 595, 595), # Juz 30
    (92, "Al-Layl", 21, 596, 596), # Juz 30
    (93, "Ad-Duha", 11, 596, 597), # Juz 30
    (94, "Ash-Sharh", 8, 597, 597), # Juz 30
    (95, "At-Tin", 8, 597, 598), # Juz 30
    (96, "Al-Alaq", 19, 598, 598), # Juz 30
    (97, "Al-Qadr", 5, 598, 599), # Juz 30
    (98, "Al-Bayyinah", 8, 599, 599), # Juz 30
    (99, "Az-Zalzalah", 8, 599, 600), # Juz 30
    (100, "Al-Adiyat", 11, 600, 600), # Juz 30
    (101, "Al-Qari'ah", 11, 600, 601), # Juz 30
    (102, "At-Takathur", 8, 601, 601), # Juz 30
    (103, "Al-Asr", 3, 601, 602), # Juz 30
    (104, "Al-Humazah", 9, 602, 602), # Juz 30
    (105, "Al-Fil", 5, 602, 603), # Juz 30
    (106, "Quraysh", 4, 603, 603), # Juz 30
    (107, "Al-Ma'un", 7, 603, 603), # Juz 30
    (108, "Al-Kawthar", 3, 603, 604), # Juz 30
    (109, "Al-Kafirun", 6, 604, 604), # Juz 30
    (110, "An-Nasr", 3, 604, 604), # Juz 30
    (111, "Al-Masad", 5, 604, 604), # Juz 30
    (112, "Al-Ikhlas", 4, 604, 604), # Juz 30
    (113, "Al-Falaq", 5, 604, 604), # Juz 30
    (114, "An-Nas", 6, 604, 604) # Juz 30
]

def seed_surahs():
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(models.Surah).first():
            print("Surahs table already populated.")
            return

        for s_id, name, ayahs, start, end in SURAH_DATA:
            surah = models.Surah(
                id=s_id,
                name=name,
                total_ayahs=ayahs,
                start_page=start,
                end_page=end
            )
            db.add(surah)
        
        db.commit()
        print(f"Successfully seeded {len(SURAH_DATA)} surahs.")
    except Exception as e:
        print(f"Error seeding surahs: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_surahs()