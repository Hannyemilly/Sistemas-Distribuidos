def comparar_vetores(vc1, vc2):
    """
    Compara dois relógios vetoriais para determinar a relação causal entre eles.
    
    Args:
        vc1 (list): Primeiro relógio vetorial
        vc2 (list): Segundo relógio vetorial
    
    Returns:
        str: Relação causal entre os vetores:
             - "antes": vc1 aconteceu antes de vc2 (vc1 → vc2)
             - "depois": vc1 aconteceu depois de vc2 (vc2 → vc1)
             - "concorrente": eventos são concorrentes (vc1 || vc2)
    """
    if len(vc1) != len(vc2):
        raise ValueError("Os relógios vetoriais devem ter o mesmo tamanho")
    
    # Verifica se vc1 ≤ vc2 (vc1[i] ≤ vc2[i] para todo i)
    vc1_menor_igual = all(vc1[i] <= vc2[i] for i in range(len(vc1)))
    
    # Verifica se vc2 ≤ vc1 (vc2[i] ≤ vc1[i] para todo i)
    vc2_menor_igual = all(vc2[i] <= vc1[i] for i in range(len(vc2)))
    
    # Verifica se existe pelo menos uma posição onde vc1[i] < vc2[i]
    existe_menor = any(vc1[i] < vc2[i] for i in range(len(vc1)))
    
    # Verifica se existe pelo menos uma posição onde vc2[i] < vc1[i]
    existe_maior = any(vc2[i] < vc1[i] for i in range(len(vc2)))
    
    if vc1_menor_igual and existe_menor:
        # vc1 → vc2 (vc1 aconteceu antes de vc2)
        return "antes"
    elif vc2_menor_igual and existe_maior:
        # vc2 → vc1 (vc1 aconteceu depois de vc2)
        return "depois"
    else:
        # vc1 || vc2 (eventos são concorrentes)
        return "concorrente"


def exibir_comparacao(evento1_info, evento2_info, relacao):
    """
    Exibe o resultado da comparação entre dois eventos de forma formatada.
    
    Args:
        evento1_info (dict): Informações do primeiro evento
        evento2_info (dict): Informações do segundo evento
        relacao (str): Relação causal entre os eventos
    """
    print("\n" + "="*60)
    print("ANÁLISE DE CAUSALIDADE")
    print("="*60)
    
    print(f"Evento 1: {evento1_info['nome']}")
    print(f"  Relógio Vetorial: {evento1_info['relogio']}")
    
    print(f"Evento 2: {evento2_info['nome']}")
    print(f"  Relógio Vetorial: {evento2_info['relogio']}")
    
    if relacao == "antes":
        print(f"\n✅ RESULTADO: O evento '{evento1_info['nome']}' aconteceu ANTES do evento '{evento2_info['nome']}'")
        print("   (Existe uma relação de causalidade: evento1 → evento2)")
    elif relacao == "depois":
        print(f"\n✅ RESULTADO: O evento '{evento1_info['nome']}' aconteceu DEPOIS do evento '{evento2_info['nome']}'")
        print("   (Existe uma relação de causalidade: evento2 → evento1)")
    else:
        print(f"\n🔄 RESULTADO: Os eventos '{evento1_info['nome']}' e '{evento2_info['nome']}' são CONCORRENTES")
        print("   (Não existe relação de causalidade entre eles)")
    
    print("="*60)