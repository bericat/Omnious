Shader "Ominous/Video Glass"
{
    // Cristal de ventana: casi invisible de frente y con un reflejo discreto al mirarlo de lado.
    Properties
    {
        _Tint ("Tinte", Color) = (0.55,0.62,0.66,1)
        _Base ("Opacidad de frente", Range(0,1)) = 0.05
        _Edge ("Reflejo de lado", Range(0,1)) = 0.3
    }
    SubShader
    {
        Tags { "RenderType"="Transparent" "RenderPipeline"="UniversalPipeline" "Queue"="Transparent" }
        Pass
        {
            Name "ForwardLit"
            Tags { "LightMode"="UniversalForward" }
            Blend SrcAlpha OneMinusSrcAlpha
            ZWrite Off
            Cull Off
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            CBUFFER_START(UnityPerMaterial)
                half4 _Tint;
                float _Base;
                float _Edge;
            CBUFFER_END
            struct V { float4 p : SV_POSITION; float3 ws : TEXCOORD0; float3 n : TEXCOORD1; };
            V Vert(float4 p : POSITION, float3 n : NORMAL)
            {
                V o; o.ws = TransformObjectToWorld(p.xyz); o.p = TransformWorldToHClip(o.ws); o.n = TransformObjectToWorldNormal(n);
                return o;
            }
            half4 Frag(V i) : SV_Target
            {
                float3 v = normalize(GetCameraPositionWS() - i.ws);
                float f = pow(1.0 - abs(dot(normalize(i.n), v)), 3.0);
                return half4(_Tint.rgb * 0.22, saturate(_Base + _Edge * f));
            }
            ENDHLSL
        }
    }
}
