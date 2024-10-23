import sys
import os
import streamlit as st
import streamlit.components.v1 as components

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from deuces.card import Card
from deuces.deck import Deck
from deuces.evaluator import Evaluator

from preflop import preflop_monte_carlo
from hse import hse_1
from hp import HandPotential_1, HandPotential_2
from percentage_rank import percentage_rank
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from odds import mc_odds_calculator

svg_card_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'svg_cards'))

image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources', 'preflop.png'))

if 'page' not in st.session_state:
    st.session_state.page = "Poker Hand Data"

page = st.sidebar.selectbox(
    "Choose a Page",
    ["Poker Hand Data", "Dashboard"],
    index=["Poker Hand Data", "Dashboard"].index(st.session_state.page)
)

if page != st.session_state.page:
    st.session_state.page = page
    st.rerun()
    
st.markdown("""
    <style>
    /* Header animation and styling */
    @keyframes gradientAnimation {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }

    .main-header {
        background-color: #5994a3;
        background-image: url(https://www.transparenttextures.com/patterns/cubes.png);
        border-radius: 12px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
        font-size: 45px;
        font-weight: bold;
        color: white;
        text-align: center;
        padding: 0px;
        margin-bottom: 0px;
        margin-top: -30px;
    }

    /* Custom styling for containers to simulate columns */
    .custom-container {
        padding: 20px;
        border-radius: 20px;
        border: 4px solid #ccc;
        box-shadow: 2px 4px 10px rgba(0, 0, 0, 0.5);
        background: #efebeb;
        margin: 10px;
    }

    /* Button styling */
    div.stButton > button:first-child {
        background-color: #007BFF;
        color: yellow;
        height: 4em;
        width: 16em;
        border-radius: 10px;
        border: 2px solid #007BFF;
        font-size: 16px;
        font-weight: bold;
        transition: background-color 0.5s ease;
        display: flex;
        # justify-content: center;
        # margin-left: 50%;
        margin: 0 auto;
        justify-content: center;
    }
    
    /* Subheader styling */
    .subheader-container {
        display: flex;
        justify-content: center;
        width: 100%;
        margin-top: -36px;
    }

    .subheader {
        font-size: 30px;
        font-weight: 500;
        color: #f08222;
        margin: 20px auto;
        padding-left: 20px;
        padding-right: 20px;
        background-color: #f0f0f0;
        border-radius: 12px;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
    }

    div.stButton > button:hover {
        background-color: #FF69B4;
        border-color: #FF69B4;
        color:white;
    }

    /* Divider styling */
    .thick-divider {
        border-top: 10px solid blue;
        margin: 5px 0;
    }

    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header"><span class="gradient-text">Poker Analytics</span></div>', unsafe_allow_html=True)
st.markdown('<hr class="thick-divider">', unsafe_allow_html=True)

def customer_base_page():    
    
    def add_bg_from_url():
        st.markdown(
            f"""
            <style>
            .stApp{{
                background-color: #e9eff5;
                background-image: url(https://www.transparenttextures.com/patterns/cubes.png);
                background-attachment: scroll;
            }}
            </style>
            """, unsafe_allow_html=True
        )
    
    add_bg_from_url()
    
    st.markdown('<div class="subheader-container"><div class="subheader">Poker Hand Data</div></div>', unsafe_allow_html=True)

    with st.expander("Instructions for this Page"):
        st.write("""
        ### Welcome to the Poker Hand Data Page

        This page allows you to explore poker hands by manually entering card combinations for both the Hero (you) and the Villain (your opponent). You'll also be able to enter community cards (flop, turn, and river), and the system will calculate hand strength and display potential outcomes for your hand to get better or worse. Below are detailed instructions for navigating the page:

        #### 1. **Entering Your Cards**
        - **Hero's Hand and Villain's Hand:** Use the sidebar to input the two hole cards for both Hero and Villain.
        - Cards are entered using the format **RankSuit** where:
        - **Rank** refers to the value of the card, which can be:
        - "2", "3", "4", "5", "6", "7", "8", "9", "T" (for 10), "J" (Jack), "Q" (Queen), "K" (King), "A" (Ace).
        - **Suit** refers to the suit of the card, which can be:
        - "c" (Clubs), "d" (Diamonds), "h" (Hearts), "s" (Spades).

        For example, **7c** means Seven of Clubs, and **Ah** means Ace of Hearts.

        #### 2. **Setting the Community Cards**
        - **Flop Cards:** After you input your hand, use the sidebar to input the three flop cards.
        - **Turn and River:** Next, input the turn card and river card to complete the board. These community cards will be displayed on the main screen.

        #### 3. **Resetting Hands**
        - If you'd like to reset all cards to experiment with a new hand, click the **Reset All** button in the sidebar. This will clear your input and let you start fresh with new cards.
        
        #### 4. **Monte Carlo Simulation for Preflop Hands**
        - For preflop , a Monte Carlo simulation (100,000 iterations) will run to estimate your chances of winning based on your current hand.
        - This simulation shows you the winning percentage for your hand before the community cards are dealt, helping you decide whether to fold or proceed.

        #### 5. **Evaluating Hand Strength**
        - Once you enter the hands and community cards, the system automatically calculates the hand strength for both the Hero and Villain.
        - The page shows the hand ranking class (e.g., Two Pair, Full House) and the numerical strength (lower rank is better, with 1 being the strongest).

        #### 6. **Visualizing the Best Hands**
        - The page will display both Hero's and Villain's best five-card hands, showing you which cards create the highest-ranking combination for each player.
        - A visualization of the hand strength changes will be provided across different stages: **Flop**, **Turn**, and **River** (depending on how many community cards you enter).

        #### 7. **Understanding Potential (Ppot and Npot)**
        - The page will calculate your hand's **Positive Potential (Ppot)** and **Negative Potential (Npot)** during the flop (two-card lookahead) and turn (one-card lookahead), letting you know if your hand has potential to improve or deteriorate based on the upcoming cards.
        - The **Effective Hand Strength (EHS)** metric will also be displayed, combining both HSE and potential.

        #### 8. **Best Hand Display**
        - Finally, the best hand for both players will be displayed in order of card strength, providing a clear picture of which hand is superior.

        #### 9. **Download Poker Report**
        - You can download the PDF report summarizing the poker analysis by clicking the button below. It will be beneficial to read the examples in the report to understand all the terms.
        
        ### Tips for Optimal Use:
        - Be sure to input the correct card strings to avoid errors.
        - Make sure you don't enter duplicate cards.
        - Experiment with different combinations to understand how hand rankings change as new cards are revealed.
        - Allow the app to finish running when you make a query - it iterates through 100,000 scenarios for Monte Carlo and the remaining outcomes for 1-card/2-card lookahead potentials.
        - Use the **Reset All** button liberally to try new hands and scenarios.
    
        """        
        )
        
    pdf_path = "Poker_Report.pdf"

    with open(pdf_path, "rb") as pdf_file:
        PDFbyte = pdf_file.read()

    st.download_button(label="Download Poker Report PDF",
                    data=PDFbyte,
                    file_name="yourfile.pdf",
                    mime='application/octet-stream')
        
    st.divider()
    
    if 'hero_card1' not in st.session_state:
        st.session_state['hero_card1'] = 'Js'
    if 'hero_card2' not in st.session_state:
        st.session_state['hero_card2'] = '9s'
    if 'villain_card1' not in st.session_state:
        st.session_state['villain_card1'] = 'Qd'
    if 'villain_card2' not in st.session_state:
        st.session_state['villain_card2'] = 'Qc'
    if 'flop_card1' not in st.session_state:
        st.session_state['flop_card1'] = 'Ks'
    if 'flop_card2' not in st.session_state:
        st.session_state['flop_card2'] = 'Qs'
    if 'flop_card3' not in st.session_state:
        st.session_state['flop_card3'] = 'Th'
    if 'turn_card' not in st.session_state:
        st.session_state['turn_card'] = 'Qh'
    if 'river_card' not in st.session_state:
        st.session_state['river_card'] = 'Ts'

    hero_card1 = st.session_state['hero_card1']
    hero_card2 = st.session_state['hero_card2']
    villain_card1 = st.session_state['villain_card1']
    villain_card2 = st.session_state['villain_card2']
    flop_card1 = st.session_state['flop_card1']
    flop_card2 = st.session_state['flop_card2']
    flop_card3 = st.session_state['flop_card3']
    turn_card = st.session_state['turn_card']
    river_card = st.session_state['river_card']
    
    def check_duplicates(cards):
        """Checks for duplicate cards in the list of card strings."""
        return len(cards) != len(set(cards)) 

    
    def display_card_image(card_string, col):
        rank_map = {
            "2": "2", "3": "3", "4": "4", "5": "5", "6": "6", "7": "7", "8": "8", "9": "9", "T": "10",
            "J": "jack", "Q": "queen", "K": "king", "A": "ace"
        }
        suit_map = {
            "c": "clubs", "d": "diamonds", "h": "hearts", "s": "spades"
        }

        rank = card_string[:-1]  
        suit = card_string[-1]   

        rank_full = rank_map.get(rank, rank)  
        suit_full = suit_map.get(suit, "")    

        card_file_name = f"{rank_full}_of_{suit_full}.svg"
        card_image_path = os.path.join(svg_card_path, card_file_name)

        try:
            col.image(card_image_path, width=140)  
        except FileNotFoundError:
            col.write(f"Card image for {card_string} not found!")
    
    def validate_card(card):
        valid_ranks = {'2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A'}
        valid_suits = {'c', 'd', 'h', 's'}

        if len(card) != 2:
            return False
        rank, suit = card[0], card[1]
        return rank in valid_ranks and suit in valid_suits
            
    st.sidebar.header("Hero's Hand")
    hero_card1 = st.sidebar.text_input("Hero's first card (e.g., '5c')", hero_card1, key="hero_card10")
    hero_card2 = st.sidebar.text_input("Hero's second card (e.g., 'Jd')", hero_card2, key="hero_card20")

    if hero_card1 and not validate_card(hero_card1):
        st.sidebar.error("Invalid format for Hero's first card. Please enter a valid card (e.g., '5c').")
    if hero_card2 and not validate_card(hero_card2):
        st.sidebar.error("Invalid format for Hero's second card. Please enter a valid card (e.g., 'Jd').")
        
        
    st.sidebar.header("Villain's Hand")
    villain_card1 = st.sidebar.text_input("Villain's first card (e.g., '5h')", villain_card1, key = "villain_card10")
    villain_card2 = st.sidebar.text_input("Villain's second card (e.g., '6s')", villain_card2, key = "villain_card20")

    if villain_card1 and not validate_card(villain_card1):
        st.sidebar.error("Invalid format for Villain's first card. Please enter a valid card (e.g., '5h').")
    if villain_card2 and not validate_card(villain_card2):
        st.sidebar.error("Invalid format for Villain's second card. Please enter a valid card (e.g., '6s').")


    st.sidebar.header("Community Cards")
    flop_card1 = st.sidebar.text_input("Flop card 1 (e.g., '3c')", flop_card1, key = "flop_card10")
    flop_card2 = st.sidebar.text_input("Flop card 2 (e.g., 'Kc')", flop_card2, key = "flop_card20")
    flop_card3 = st.sidebar.text_input("Flop card 3 (e.g., '5s')", flop_card3, key = "flop_card30")
    turn_card = st.sidebar.text_input("Turn card (e.g., '7h')", turn_card, key = "turn_card1")
    river_card = st.sidebar.text_input("River card (e.g., 'As')", river_card, key = "river_card2")
    st.sidebar.caption("""
        Ensure that you enter the Flop before the Turn and River - order is always Flop, Turn, and then River.
        """)
    
    if flop_card1 and not validate_card(flop_card1):
        st.sidebar.error("Invalid format for Flop card 1. Please enter a valid card (e.g., '3c').")
    if flop_card2 and not validate_card(flop_card2):
        st.sidebar.error("Invalid format for Flop card 2. Please enter a valid card (e.g., 'Kc').")
    if flop_card3 and not validate_card(flop_card3):
        st.sidebar.error("Invalid format for Flop card 3. Please enter a valid card (e.g., '5s').")
    if turn_card and not validate_card(turn_card):
        st.sidebar.error("Invalid format for Turn card. Please enter a valid card (e.g., '7h').")
    if river_card and not validate_card(river_card):
        st.sidebar.error("Invalid format for River card. Please enter a valid card (e.g., 'As').")

    all_cards = [hero_card1, hero_card2, villain_card1, villain_card2, flop_card1, flop_card2, flop_card3, turn_card, river_card]

    all_cards = [card for card in all_cards if card]
    
    main_col_1, main_col_2 = st.columns([1, 1])
    
    if check_duplicates(all_cards):
        st.error("Duplicate cards detected! Please ensure all cards are unique.")
    else:

        with main_col_1:
            st.markdown("<h3 style='text-align: center;'>Hero's Hand</h3>", unsafe_allow_html=True)
            col1, col2, = st.columns([1, 1])  

            if hero_card1:
                with col1:
                    display_card_image(hero_card1, st)

            if hero_card2:
                with col2:
                    display_card_image(hero_card2, st)
                    
        with main_col_2:
            st.markdown("<h3 style='text-align: center;'>Villain's Hand</h3>", unsafe_allow_html=True)

            col3, col4 = st.columns([1, 1])

            if villain_card1:
                with col3:
                    display_card_image(villain_card1, st)

            if villain_card2:
                with col4:
                    display_card_image(villain_card2, st)
        
        
        if st.sidebar.button("Reset All", key="reset_button10"):
            # Reset all session state values
            st.session_state['hero_card1'] = ''
            st.session_state['hero_card2'] = ''
            st.session_state['villain_card1'] = ''
            st.session_state['villain_card2'] = ''
            st.session_state['flop_card1'] = ''
            st.session_state['flop_card2'] = ''
            st.session_state['flop_card3'] = ''
            st.session_state['turn_card'] = ''
            st.session_state['river_card'] = ''
            st.rerun()

        st.markdown("<h3 style='text-align: center;'>Community Cards (Flop, Turn, River)</h3>", unsafe_allow_html=True)
        col_flop1, col_flop2, col_flop3, col_turn, col_river = st.columns([1, 1, 1, 1, 1])

        if flop_card1:
            with col_flop1:
                display_card_image(flop_card1, st)
        
        if flop_card2:
            with col_flop2:
                display_card_image(flop_card2, st)
    
        if flop_card3:  
            with col_flop3:
                display_card_image(flop_card3, st)

        if flop_card1 and flop_card2 and flop_card3:
            if turn_card:
                with col_turn:
                    display_card_image(turn_card, st)
        elif turn_card and not flop_card1 and not flop_card2 and not flop_card3:
            st.write("where's the flop? :)")
        
        if turn_card and river_card:
            with col_river:
                display_card_image(river_card, st)
        elif not turn_card and river_card:
            with col_river:
                st.write("there has to be a turn for a river!")
                
        st.divider()

        hero_hand = []
        villain_hand = []
        board = []
        hero_rank = None
        villain_rank = None
        
        if hero_card1 and hero_card2:
            hero_hand = [Card.new(hero_card1), Card.new(hero_card2)]
        if villain_card1 and villain_card2:
            villain_hand = [Card.new(villain_card1), Card.new(villain_card2)]
            
        if flop_card1 and flop_card2 and flop_card3:
            board = [Card.new(flop_card1), Card.new(flop_card2), Card.new(flop_card3)]

        if turn_card:
            board.append(Card.new(turn_card))

        if river_card:
            board.append(Card.new(river_card))
            
        sub_col_1, sub_col_2 = st.columns([1, 1])

        with sub_col_1:
            st.subheader("**Hero's Preflop Monte Carlo**")

            if hero_hand:
                results = preflop_monte_carlo(hero_hand, 2)

                for result in results:
                    st.write(f"Opponents: {result['opponents']}")
                    st.write(f"Wins: {result['wins']}")
                    st.write(f"Losses: {result['losses']}")
                    st.write(f"Ties: {result['ties']}")
                    st.write(f"**Monte Carlo Income Rate:** {result['mc_IR']:.2f}")
            
            if hero_hand and villain_hand:
                st.write("### Odds Calculation")
                hero_win_percentage, villain_win_percentage = mc_odds_calculator(hero_hand, villain_hand)
                st.write(f"**Hero's Win Percentage:** {hero_win_percentage * 100:.2f}%")
                st.write(f"**Villain's Win Percentage:** {villain_win_percentage * 100:.2f}%")

        with sub_col_2:
            st.subheader("**Villain's Preflop Monte Carlo**")
            if villain_hand:
                more_results = preflop_monte_carlo(villain_hand, 2)
                for result in more_results:
                    st.write(f"Opponents: {result['opponents']}")
                    st.write(f"Wins: {result['wins']}")
                    st.write(f"Losses: {result['losses']}")
                    st.write(f"Ties: {result['ties']}")
                    st.write(f"**Monte Carlo Income Rate:** {result['mc_IR']:.2f}")
        

            evaluator = Evaluator()

            if len(board) >=3 and hero_hand and villain_hand and board:
                st.write("### Hand Rankings")
                hero_rank = evaluator.evaluate(board, hero_hand)
                villain_rank = evaluator.evaluate(board, villain_hand)

                st.write(f"**Hero's hand rank:** {percentage_rank(board, hero_hand)}")
                st.write(f"**Villain's hand rank:** {percentage_rank(board, villain_hand)}")
            
        best_hero_hand = []
        best_villain_hand = []

        st.divider()
        
        if hero_hand and villain_hand and board and len(hero_hand + board) >= 5 and len(villain_hand + board) >= 5:
            st.write("### Hand Comparions")
            best_hero_hand = evaluator.get_best_hand(hero_hand + board, [])
            best_villain_hand = evaluator.get_best_hand(villain_hand + board, [])
        else:
            st.markdown("<h3 style='text-align: center; color: red;'>Make sure there's at least a flop for best hand comparison.</h3>", unsafe_allow_html=True)
            best_hero_hand = []
            best_villain_hand = []

        def sort_hand_by_rank(hand):
            return sorted(hand, key=lambda card: Card.get_rank_int(card))

        
        if best_hero_hand and best_villain_hand:
            sorted_hero_hand = sort_hand_by_rank(best_hero_hand)
            sorted_villain_hand = sort_hand_by_rank(best_villain_hand)

        if hero_hand and villain_hand and best_hero_hand and best_villain_hand:
            hero_rank = evaluator.evaluate(board, hero_hand)
            hero_rank_class = evaluator.get_rank_class(hero_rank)
            hero_hand_string = evaluator.class_to_string(hero_rank_class)

            villain_rank = evaluator.evaluate(board, villain_hand)
            villain_rank_class = evaluator.get_rank_class(villain_rank)
            villain_hand_string = evaluator.class_to_string(villain_rank_class)

            st.write(f"**Hero's Best Hand** ({hero_hand_string})")
            hero_col1, hero_col2, hero_col3, hero_col4, hero_col5 = st.columns(5)
            for i, card in enumerate(sorted_hero_hand):
                with locals()[f"hero_col{i+1}"]:
                    display_card_image(Card.int_to_str(card), st)

            st.write(f"**Villain's Best Hand** ({villain_hand_string})")
            villain_col1, villain_col2, villain_col3, villain_col4, villain_col5 = st.columns(5)
            for i, card in enumerate(sorted_villain_hand):
                with locals()[f"villain_col{i+1}"]:
                    display_card_image(Card.int_to_str(card), st)

        if hero_rank and villain_rank:
            if hero_rank < villain_rank:
                st.markdown("<h2 style='text-align: center; color: green;'>Hero wins!</h2>", unsafe_allow_html=True)
            elif hero_rank > villain_rank:
                st.markdown("<h2 style='text-align: center; color: red;'>Villain wins!</h2>", unsafe_allow_html=True)
            else:
                st.markdown("<h2 style='text-align: center; color: blue;'>It's a tie!</h2>", unsafe_allow_html=True)

        st.divider()
        
        if hero_hand and villain_hand and board:
            st.write("### Hand Strength Evaluation (HSE)")
            hse_hero = hse_1(board, hero_hand)
            hse_villain = hse_1(board, villain_hand)

            st.write(f"**Hero's HSE:** {hse_hero['hse']:.2f}")
            st.write(f"Wins: {hse_hero['wins']}, Losses: {hse_hero['losses']}, Ties: {hse_hero['ties']}")


            st.write(f"**Villain's HSE:** {hse_villain['hse']:.2f}")
            st.write(f"Wins: {hse_villain['wins']}, Losses: {hse_villain['losses']}, Ties: {hse_villain['ties']}")

            if not turn_card and river_card:
                st.markdown("<h3 style='text-align: center; color: purple;'>Make sure you select a turn card before river!</h3>", unsafe_allow_html=True)
            elif turn_card and not river_card:
                pp_1, np_1, hero_HPTotal = HandPotential_1(board, hero_hand)
                pp_2, np_2, villain_HPTotal = HandPotential_1(board, villain_hand)
                
                st.write("### Hand Potentials and Effective Hand Strength (EHS)")

                col1, col2 = st.columns([1, 1])
                with col1:
                    st.write(f"**Hero's Positive Potential - 1 Card Lookahead(Ppot):** {pp_1:.2f}")
                    st.write(f"**Hero's Negative Potential - 1 Card Lookahead(Npot):** {np_1:.2f}")
                    st.write(f"**Hero's Effective Hand Strength (EHS):** {hse_hero['hse'] + (1 - hse_hero['hse']) * pp_1}")
                    st.write(f"**HPTotal:** {hero_HPTotal}")


                with col2:
                    st.write(f"**Villain's Positive Potential - 1 Card Lookahead(Ppot):** {pp_2:.2f}")
                    st.write(f"**Villain's Negative Potential - 1 Card Lookahead(Npot):** {np_2:.2f}")
                    st.write(f"**Villain's Effective Hand Strength (EHS):** {hse_villain['hse'] + (1 - hse_villain['hse']) * pp_2}")     
                    st.write(f"**HPTotal:** {villain_HPTotal}")
                    
                st.caption("""
                **Hand Potentials: 1-Card Lookahead, 2-Card Lookahead, and HPTotal**

                - **1-Card Lookahead**: Evaluates the potential outcomes if one more community card is dealt. It checks how Hero's and Villain's hands compare after this single card is added, calculating the probability of improving (Ppot) or falling behind (Npot).

                - **2-Card Lookahead**: Looks ahead to the remaining two community cards, predicting how Hero's and Villain's hands might change after both cards are dealt. It provides a more comprehensive view of potential outcomes.

                - **HPTotal**: Tracks all possible future scenarios, showing how often Hero’s hand is ahead, tied, or behind after considering every potential next card(s). It forms the basis for calculating both Ppot and Npot by summarizing these scenarios.
                
                - **Effective Hand Strength:** It is calculated using both Hand Strength and Positive Potential (EHS = HS + (1 − HS ) · Ppot).
                """)
                
            elif not (turn_card and river_card):
                pp_1, np_1, hero_HPTotal = HandPotential_2(board, hero_hand)
                pp_2, np_2, villain_HPTotal = HandPotential_2(board, villain_hand)

                st.write("### Hand Potentials and Effective Hand Strength (EHS)")
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.write(f"**Hero's Positive Potential - 2 Card Lookahead(Ppot):** {pp_1:.2f}")
                    st.write(f"**Hero's Negative Potential - 2 Card Lookahead(Npot):** {np_1:.2f}")
                    st.write(f"**Hero's Effective Hand Strength (EHS):** {hse_hero['hse'] + (1 - hse_hero['hse']) * pp_1}")
                    st.write(f"**HPTotal:** {hero_HPTotal}")


                with col2:
                    st.write(f"**Villain's Positive Potential - 2 Card Lookahead(Ppot):** {pp_2:.2f}")
                    st.write(f"**Villain's Negative Potential - 2 Card Lookahead(Npot):** {np_2:.2f}")
                    st.write(f"**Villain's Effective Hand Strength (EHS):** {hse_villain['hse'] + (1 - hse_villain['hse']) * pp_2}")
                    st.write(f"**HPTotal:** {villain_HPTotal}")

                st.caption("""
                **Hand Potentials: 1-Card Lookahead, 2-Card Lookahead, and HPTotal**

                - **1-Card Lookahead**: Evaluates the potential outcomes if one more community card is dealt. It checks how Hero's and Villain's hands compare after this single card is added, calculating the probability of improving (Ppot) or falling behind (Npot).

                - **2-Card Lookahead**: Looks ahead to the remaining two community cards, predicting how Hero's and Villain's hands might change after both cards are dealt. It provides a more comprehensive view of potential outcomes.

                - **HPTotal**: Tracks all possible future scenarios, showing how often Hero’s hand is ahead, tied, or behind after considering every potential next card(s). It forms the basis for calculating both Ppot and Npot by summarizing these scenarios.
                
                - **Effective Hand Strength:** It is calculated using both Hand Strength and Positive Potential (EHS = HS + (1 − HS ) · Ppot).
                """)

            else:
                st.markdown("<h3 style='text-align: center; color: blue;'>Make sure turn and river are not both selected to see positive potentials 1 and 2.</h3>", unsafe_allow_html=True)
        
        st.session_state['hero_card1'] = hero_card1
        st.session_state['hero_card2'] = hero_card2
        st.session_state['villain_card1'] = villain_card1
        st.session_state['villain_card2'] = villain_card2
        st.session_state['flop_card1'] = flop_card1
        st.session_state['flop_card2'] = flop_card2
        st.session_state['flop_card3'] = flop_card3
        st.session_state['turn_card'] = turn_card
        st.session_state['river_card'] = river_card
        
        st.divider()
    
def dashboard():    
    def add_bg_from_url():
        st.markdown(
            f"""
            <style>
            .stApp{{
                background-color: #e9eff5;
                background-image: url(https://www.transparenttextures.com/patterns/cubes.png);
                background-attachment: scroll;
            }}
            </style>
            """, unsafe_allow_html=True
        )
    
    add_bg_from_url()
    
    st.markdown('<div class="subheader-container"><div class="subheader">Poker Dashboard</div></div>', unsafe_allow_html=True)

    def display_card_image(card_string, col):
        rank_map = {
            "2": "2", "3": "3", "4": "4", "5": "5", "6": "6", "7": "7", "8": "8", "9": "9", "T": "10",
            "J": "jack", "Q": "queen", "K": "king", "A": "ace"
        }
        suit_map = {
            "c": "clubs", "d": "diamonds", "h": "hearts", "s": "spades"
        }

        rank = card_string[:-1]  
        suit = card_string[-1]   

        rank_full = rank_map.get(rank, rank)  
        suit_full = suit_map.get(suit, "")    

        
        card_file_name = f"{rank_full}_of_{suit_full}.svg"
        card_image_path = os.path.join(svg_card_path, card_file_name)

        try:
            col.image(card_image_path, width=140)  
        except FileNotFoundError:
            col.write(f"Card image for {card_string} not found!")
    
    
    
    def plot_preflop_income_rate():
        hands = [
            'AAo', 'KKo', 'QQo', 'JJo', 'TTo', '99o', '88o', 'AKs', '77o', 'AQs',
        ]

        df = pd.read_csv('src/preflop_equity.csv', header=None)

        x = np.arange(2, 11)  
        
        selected_rows = df[df[0].isin(hands)]

        hands2 = selected_rows.iloc[:, 0].tolist()

        y = np.array(selected_rows.iloc[:, 1:])

        if y.shape[1] > len(x):
            y = y[:, :len(x)]  
            
        y = np.array([list(map(lambda val: float(val[:-1]), row)) for row in y])

        plt.figure(figsize=(10, 6))
        plt.xlabel('Number of Players')
        plt.ylabel('Income Rate')
        plt.title('Preflop Income Rate vs. Number of Players')
        plt.yticks(np.arange(0, 101, 5))

        for i in range(len(hands2)):
            plt.plot(x, y[i], linestyle=('-' if y[i][0] > 50 else '--'), label=hands2[i], marker='o')

        plt.legend()

        st.pyplot(plt)

    plot_preflop_income_rate()
    
    st.caption("""
    In the above dashboard, the top 10 hands from the Sklansky-Karlson hand rankings are selected. 
    This graph indicates the decrease in Income Rates (IR) for these hands as the number of players at the table increases. 
    There are some interesting trends we can notice from the outcome:

    - Pocket Aces remains the strongest holding with any number of players at the table. No line ever surpasses the blue line, which represents AA.
    - AKs (Ace-King suited) becomes stronger as the number of players increases, jumping from 8th rank in a 2-player game to 4th rank in a 10-player game. This trend supports why professional players are willing to go all-in with AKs when there are at least 6 players at the table.
    - The graph also supports the common poker saying that JJ vs AKs is a coin flip when there are 6 or more players at the table.

    These trends provide deeper insight into poker strategies for multi-player games.
    """)

    
    st.divider()
        
    def calculate_hand_strength(board, hand):
        evaluator = Evaluator()
        hand_strength = evaluator.evaluate(board, hand)
        return hand_strength

    def real_time_hand_strength(hero_hand, villain_hand, board):
        evaluator = Evaluator()

        hero_strengths = []
        villain_strengths = []
        hero_rank_classes = []
        villain_rank_classes = []

        hero_strengths.append(0)  
        villain_strengths.append(0)
        hero_rank_classes.append("Pre-flop")
        villain_rank_classes.append("Pre-flop")

        if len(board) >= 3:
            hero_strength = evaluator.evaluate(board[:3], hero_hand)
            villain_strength = evaluator.evaluate(board[:3], villain_hand)
            hero_strengths.append(hero_strength)
            villain_strengths.append(villain_strength)

            hero_rank_classes.append(evaluator.class_to_string(evaluator.get_rank_class(hero_strength)))
            villain_rank_classes.append(evaluator.class_to_string(evaluator.get_rank_class(villain_strength)))
        
        if len(board) >= 4:
            hero_strength = evaluator.evaluate(board[:4], hero_hand)
            villain_strength = evaluator.evaluate(board[:4], villain_hand)
            hero_strengths.append(hero_strength)
            villain_strengths.append(villain_strength)

            hero_rank_classes.append(evaluator.class_to_string(evaluator.get_rank_class(hero_strength)))
            villain_rank_classes.append(evaluator.class_to_string(evaluator.get_rank_class(villain_strength)))

        if len(board) == 5:
            hero_strength = evaluator.evaluate(board, hero_hand)
            villain_strength = evaluator.evaluate(board, villain_hand)
            hero_strengths.append(hero_strength)
            villain_strengths.append(villain_strength)

            hero_rank_classes.append(evaluator.class_to_string(evaluator.get_rank_class(hero_strength)))
            villain_rank_classes.append(evaluator.class_to_string(evaluator.get_rank_class(villain_strength)))

        return hero_strengths, villain_strengths, hero_rank_classes, villain_rank_classes

    def plot_hand_strength(hero_strengths, villain_strengths):
        stages = ['Flop', 'Turn', 'River'] 
        
        x = np.arange(len(hero_strengths)) 

        plt.figure(figsize=(10, 6))

        plt.plot(x, hero_strengths, marker='o', linestyle='-', color='blue', label="Hero's Hand Strength")
        
        plt.plot(x, villain_strengths, marker='o', linestyle='-', color='red', label="Villain's Hand Strength")

        plt.xticks(x, stages[:len(hero_strengths)])  
        plt.xlabel('Poker Stages')
        plt.ylabel('Hand Strength (Rank)')
        plt.title('Real-time Hand Strength for Hero and Villain')

        plt.legend()

        st.pyplot(plt)

    def poker_hand_visualization():
        deck = Deck()

        hero_hand = deck.draw(2)
        villain_hand = deck.draw(2)

        board = deck.draw(5)

        main_column, sec_column = st.columns([1,1])
        with main_column:
            st.markdown("<h3 style='text-align: center;'>Hero's Hand</h3>", unsafe_allow_html=True)
            col1, col2 = st.columns([1, 1])
            with col1:
                display_card_image(Card.int_to_str(hero_hand[0]), st)
            with col2:
                display_card_image(Card.int_to_str(hero_hand[1]), st)
        with sec_column:
            st.markdown("<h3 style='text-align: center;'>Villain's Hand</h3>", unsafe_allow_html=True)
            col3, col4 = st.columns([1, 1])
            with col3:
                display_card_image(Card.int_to_str(villain_hand[0]), st)
            with col4:
                display_card_image(Card.int_to_str(villain_hand[1]), st)
                
        st.markdown("<h3 style='text-align: center;'>Community Cards (Flop, Turn, River)</h3>", unsafe_allow_html=True)
        col_flop1, col_flop2, col_flop3, col_turn, col_river = st.columns([1, 1, 1, 1, 1])
        with col_flop1:
            display_card_image(Card.int_to_str(board[0]), st)
        with col_flop2:
            display_card_image(Card.int_to_str(board[1]), st)
        with col_flop3:
            display_card_image(Card.int_to_str(board[2]), st)
        with col_turn:
            display_card_image(Card.int_to_str(board[3]), st)
        with col_river:
            display_card_image(Card.int_to_str(board[4]), st)
        
            
        st.divider()
        
        st.markdown("<h4 style='text-align: center;'>Hero vs Villain Hand Strength Across All Community Streets</h4>", unsafe_allow_html=True)


        hero_strengths, villain_strengths, hero_rank_classes, villain_rank_classes = real_time_hand_strength(hero_hand, villain_hand, board)

        plot_hand_strength(hero_strengths[1:], villain_strengths[1:])  

        another_col, sec_col = st.columns([1,1])
        with another_col:
            stages = ["Pre-flop", "Flop", "Turn", "River"]
            for i in range(1, len(hero_strengths)):
                st.write(f"### {stages[i]} Results")
                st.write(f"**Hero's Hand Strength (Rank):** {hero_strengths[i]}")
                st.write(f"**Villain's Hand Strength (Rank):** {villain_strengths[i]}")
                st.write(f"**Hero's Hand Rank Class:** {hero_rank_classes[i]}")
                st.write(f"**Villain's Hand Rank Class:** {villain_rank_classes[i]}")
        
        with sec_col:
            st.caption("""
            This graph illustrates the real-time changes in hand strength for both Hero and Villain throughout the community poker streets (Flop, Turn, and River). 
            The hand strength is represented by its rank, where a lower rank signifies a stronger hand, with 1 being the strongest possible hand — a Royal Flush. 
            The graph dynamically showcases how each player's hand evolves, allowing for a clear comparison of which hand holds a strategic advantage at each stage of the game.
            """)
            if st.button("Generate New Hand", key = "generate_hand"):
                st.rerun()

    poker_hand_visualization()
    
    st.divider()

if st.session_state.page == "Poker Hand Data":
    customer_base_page()
elif st.session_state.page == "Dashboard":
    dashboard()
    
